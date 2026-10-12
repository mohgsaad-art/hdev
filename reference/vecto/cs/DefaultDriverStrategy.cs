/*
* This file is part of VECTO.
*
* Copyright © 2012-2019 European Union
*
* Developed by Graz University of Technology,
*              Institute of Internal Combustion Engines and Thermodynamics,
*              Institute of Technical Informatics
*
* VECTO is licensed under the EUPL, Version 1.1 or - as soon they will be approved
* by the European Commission - subsequent versions of the EUPL (the "Licence");
* You may not use VECTO except in compliance with the Licence.
* You may obtain a copy of the Licence at:
*
* https://joinup.ec.europa.eu/community/eupl/og_page/eupl
*
* Unless required by applicable law or agreed to in writing, VECTO
* distributed under the Licence is distributed on an "AS IS" basis,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the Licence for the specific language governing permissions and
* limitations under the Licence.
*
* Authors:
*   Stefan Hausberger, hausberger@ivt.tugraz.at, IVT, Graz University of Technology
*   Christian Kreiner, christian.kreiner@tugraz.at, ITI, Graz University of Technology
*   Michael Krisper, michael.krisper@tugraz.at, ITI, Graz University of Technology
*   Raphael Luz, luz@ivt.tugraz.at, IVT, Graz University of Technology
*   Markus Quaritsch, markus.quaritsch@tugraz.at, IVT, Graz University of Technology
*   Martin Rexeis, rexeis@ivt.tugraz.at, IVT, Graz University of Technology
*/

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using TUGraz.VectoCommon.Exceptions;
using TUGraz.VectoCommon.InputData;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Configuration;
using TUGraz.VectoCore.Models.Connector.Ports.Impl;
using TUGraz.VectoCore.Models.Simulation;
using TUGraz.VectoCore.Models.Simulation.DataBus;
using TUGraz.VectoCore.Models.Simulation.Impl;
using TUGraz.VectoCore.Models.SimulationComponent.Data;
using TUGraz.VectoCore.OutputData;
using TUGraz.VectoCore.Utils;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
	public enum PCCStates
	{
		OutsideSegment,
		WithinSegment,
		UseCase1,
		UseCase2,
		PCCinterrupt
	}

	public class DefaultDriverStrategy : LoggingObject, IDriverStrategy
	{
		public static readonly SIBase<Meter> BrakingSafetyMargin = 0.1.SI<Meter>();
		protected internal DrivingBehaviorEntry NextDrivingAction;

		public enum DrivingMode
		{
			DrivingModeDrive,
			DrivingModeBrake,
		}

		protected internal DrivingMode CurrentDrivingMode;

		protected readonly Dictionary<DrivingMode, IDriverMode> DrivingModes = new Dictionary<DrivingMode, IDriverMode>();
		protected Second VehicleHaltTimestamp;
		protected Second EngineOffTimestamp;
		private VehicleData.ADASData ADAS;

		public readonly MeterPerSecond PTODriveMinSpeed;

		protected internal EcoRoll EcoRollState;
		protected PCCSegments PCCSegments;

		public PCCStates PCCState => pccState;
		protected internal PCCStates pccState = PCCStates.OutsideSegment;
		protected internal bool ATEcoRollReleaseLockupClutch;

		private readonly VectoSimulationJobType PowertrainArchitecture;

		public DefaultDriverStrategy(IVehicleContainer container)
		{
			PTODriveMinSpeed = container.RunData.DriverData.PTODriveMinSpeed;
			DrivingModes.Add(DrivingMode.DrivingModeDrive, new DriverModeDrive() { DriverStrategy = this });
			DrivingModes.Add(DrivingMode.DrivingModeBrake, new DriverModeBrake() { DriverStrategy = this });
			CurrentDrivingMode = DrivingMode.DrivingModeDrive;

			VehicleCategory = container.RunData.VehicleData.VehicleCategory;

			var data = container.RunData;
			ADAS = data?.VehicleData?.ADAS ?? new VehicleData.ADASData() {
				EcoRoll = EcoRollType.None,
				EngineStopStart = false,
				PredictiveCruiseControl = PredictiveCruiseControlType.None,
			};
			ATEcoRollReleaseLockupClutch = data?.GearboxSinglePwt?.ATEcoRollReleaseLockupClutch ?? false;

			EcoRollState = new EcoRoll {
				State = EcoRollStates.EcoRollOff,
				Gear = new GearshiftPosition(0),
				StateChangeTstmp = -double.MaxValue.SI<Second>(),
				PreviousBrakePower = 0.SI<Watt>(),
				AcceleratorPedalIdle = false,
			};

			PCCSegments = new PCCSegments();

			PowertrainArchitecture = data.JobType;
			
			if (ADAS.PredictiveCruiseControl != PredictiveCruiseControlType.None) {
				// create a dummy powertrain for pre-processing and estimations
				var testPowertrain = container.SimplePowertrainBuilder.CreateTestPowertrain(container, false, data.JobType);
				container.AddPreprocessor(new PCCSegmentPreprocessor(testPowertrain, PCCSegments, data?.DriverData.PCC));
			}
		}

		public VehicleCategory VehicleCategory { get; set; }

		public IDriverActions Driver { get; set; }

		protected IDataBus DataBus => Driver?.DataBus;

		public DrivingBehaviorEntry BrakeTrigger { get; protected internal set; }

		public IResponse Request(Second absTime, Meter ds, MeterPerSecond targetVelocity, Radian gradient)
		{
			var retVal = DoHandleRequest(absTime, ds, targetVelocity, gradient);
			if (retVal is ResponseSuccess) {
				EcoRollState.PreviousBrakePower = DataBus.Brakes.BrakePower;
				if (retVal.Source is ICombustionEngine) {
					var success = retVal as ResponseSuccess;
					var avgEngineSpeed = (success.Engine.EngineSpeed + DataBus.EngineInfo.EngineSpeed) / 2.0;
					EcoRollState.AcceleratorPedalIdle = success.Engine.DragPower.IsEqual(success.Engine.TotalTorqueDemand * avgEngineSpeed, 10.SI<Watt>());
				} else {
					EcoRollState.AcceleratorPedalIdle = false;
				}
			}
			return retVal;
		}

		public IResponse Request(Second absTime, Second dt, MeterPerSecond targetVelocity, Radian gradient)
		{
			Driver.DriverBehavior = DrivingBehavior.Halted;
			CurrentDrivingMode = DrivingMode.DrivingModeDrive;

			if (ADAS.EngineStopStart) {
				HandleEngineStopStartDuringVehicleStop(absTime);
			}

			var retVal = Driver.DrivingActionHalt(
				absTime, dt, VectoMath.Min(DataBus.VehicleInfo.MaxVehicleSpeed, targetVelocity), gradient);
			EcoRollState.PreviousBrakePower = DataBus.Brakes.BrakePower;
			return retVal;
		}

		public void WriteModalResults(IModalDataContainer container)
		{
			container.SetDataValue("EcoRollConditionsMet", EcoRollState.AllConditionsMet ? 1 : 0);
			if (PCCSegments.Count > 0) {
				var val = 0;
				if (DataBus.MileageCounter.Distance > PCCSegments.Current.EndDistance) {
					val = 0;
				} else if (DataBus.MileageCounter.Distance > PCCSegments.Current.DistanceAtLowestSpeed) {
					val = 5;
				} else if (DataBus.MileageCounter.Distance > PCCSegments.Current.StartDistance) {
					val = -5;
				}
				container.SetDataValue("PCCSegment", val);
				container.SetDataValue("PCCState", (int)pccState);
			} else {
				container.SetDataValue("PCCSegment", 0);
				container.SetDataValue("PCCState", (int)pccState);
			}
		}

		public void CommitSimulationStep()
		{
			if (PCCSegments.Count > 0) {
				if (DataBus.MileageCounter.Distance > PCCSegments.Current.EndDistance) {
					PCCSegments.MoveNext();
					pccState = PCCStates.OutsideSegment;
				}
			}
		}

		protected virtual IResponse DoHandleRequest(Second absTime, Meter ds, MeterPerSecond targetVelocity, Radian gradient)
		{
			VehicleHaltTimestamp = null;

			if (ADAS.PredictiveCruiseControl != PredictiveCruiseControlType.None) {
				HandlePCC(absTime, targetVelocity);
			}
			if (ADAS.EcoRoll != EcoRollType.None &&
				(pccState == PCCStates.OutsideSegment || pccState == PCCStates.WithinSegment)) {
				HandleEcoRoll(absTime, targetVelocity);
			}

			//if (ADAS.EcoRoll != EcoRollType.None) {
			// todo MQ: keep something like this to prevent driver to turn on engine in every timestep (in combination with hybrids leads to errors!)
			if (EcoRollState.State != EcoRollStates.EcoRollOn && pccState != PCCStates.UseCase1 &&
				pccState != PCCStates.UseCase2) {
				EngineOffTimestamp = null;
				if (DataBus.PowertrainInfo.HasCombustionEngine && !DataBus.PowertrainInfo.HasElectricMotor) {
					DataBus.EngineCtl.CombustionEngineOn = true;
				}
			}
			//}

			if (CurrentDrivingMode == DrivingMode.DrivingModeBrake) {
				var nextAction = GetNextDrivingAction(ds);
				var currentDistance = DataBus.MileageCounter.Distance;

                if (nextAction != null && !BrakeTrigger.HasEqualTrigger(nextAction) && 
					(nextAction.ActionDistance.IsSmallerOrEqual(BrakeTrigger.ActionDistance) || nextAction.BrakingStartDistance.IsBetween(currentDistance, currentDistance + ds))) {
					BrakeTrigger = nextAction;
				}
				if (DataBus.MileageCounter.Distance.IsGreaterOrEqual(BrakeTrigger.TriggerDistance, 1e-3.SI<Meter>())) {
					CurrentDrivingMode = DrivingMode.DrivingModeDrive;
					NextDrivingAction = null;
					DrivingModes[CurrentDrivingMode].ResetMode();
					Log.Debug("Switching to DrivingMode DRIVE");
				}


			}
			if (CurrentDrivingMode == DrivingMode.DrivingModeDrive) {
				var currentDistance = DataBus.MileageCounter.Distance;

				//var coasting = LookAheadCoasting(ds);

				UpdateDrivingAction(currentDistance, ds);
				if (NextDrivingAction != null) {
					var remainingDistance = NextDrivingAction.ActionDistance - currentDistance;
					var estimatedTimestep = remainingDistance / DataBus.VehicleInfo.VehicleSpeed;

					var atTriggerTistance = remainingDistance.IsEqual(
						0.SI<Meter>(), Constants.SimulationSettings.DriverActionDistanceTolerance);
					var closeBeforeBraking = estimatedTimestep.IsSmaller(Constants.SimulationSettings.LowerBoundTimeInterval);
					var brakingIntervalTooShort = NextDrivingAction.Action == DrivingBehavior.Braking &&
												((NextDrivingAction.TriggerDistance - NextDrivingAction.ActionDistance) / DataBus.VehicleInfo.VehicleSpeed)
												.IsSmaller(
													Constants.SimulationSettings.LowerBoundTimeInterval / 20) && !DataBus.ClutchesInfo.First().ClutchClosed(absTime);
					var brakingIntervalShort = NextDrivingAction.Action == DrivingBehavior.Braking &&
												NextDrivingAction.ActionDistance.IsSmaller(currentDistance + ds) &&
												((NextDrivingAction.TriggerDistance - NextDrivingAction.ActionDistance) / DataBus.VehicleInfo.VehicleSpeed)
												.IsSmaller(
													Constants.SimulationSettings.LowerBoundTimeInterval / 2) 
													&& !DataBus.PowertrainInfo.VehicleArchitecture.IsMultiplePowertrains()
													&& (DataBus.GearboxInfo().GearboxType.AutomaticTransmission() || !DataBus.ClutchesInfo.First().ClutchClosed(absTime));
					
					if (brakingIntervalShort && remainingDistance.IsEqual(ds)) {
						return new ResponseDrivingCycleDistanceExceeded(this) {
							MaxDistance = ds / 2
						};
					}
					if (atTriggerTistance || closeBeforeBraking || brakingIntervalTooShort) {
						CurrentDrivingMode = DrivingMode.DrivingModeBrake;
						DrivingModes[CurrentDrivingMode].ResetMode();
						Log.Debug("Switching to DrivingMode BRAKE");

						BrakeTrigger = NextDrivingAction;

						//break;
					} else if ((currentDistance + ds).IsGreater(NextDrivingAction.ActionDistance)) {
						Log.Debug(
							"Current simulation interval exceeds next action distance at {0}. reducing maxDistance to {1}",
							NextDrivingAction.ActionDistance, NextDrivingAction.ActionDistance - currentDistance);
						return new ResponseDrivingCycleDistanceExceeded(this) {
							MaxDistance = NextDrivingAction.ActionDistance - currentDistance
						};
					}
				}
			}

			var retVal = DrivingModes[CurrentDrivingMode].Request(
				absTime, ds, VectoMath.Min(DataBus.VehicleInfo.MaxVehicleSpeed, targetVelocity), gradient);

			return retVal;
		}

		private void HandlePCC(Second absTime, MeterPerSecond targetVelocity)
		{
			var vehicleSpeed = DataBus.VehicleInfo.VehicleSpeed;

			UpdatePCCState(targetVelocity);

			switch (pccState) {
				case PCCStates.UseCase1:
					if (vehicleSpeed <= targetVelocity - Driver.DriverData.PCC.UnderSpeed * 1.05) {
						pccState = PCCStates.PCCinterrupt;
					}
					if (vehicleSpeed >= targetVelocity + 1.KMPHtoMeterPerSecond()) {
						pccState = PCCStates.WithinSegment;
					}
					break;
				case PCCStates.UseCase2:
					if (vehicleSpeed < Driver.DriverData.PCC.MinSpeed || vehicleSpeed > targetVelocity + 1.KMPHtoMeterPerSecond()) {
						pccState = PCCStates.WithinSegment;
					}
					break;
				case PCCStates.PCCinterrupt:
					if (vehicleSpeed >= targetVelocity - Driver.DriverData.PCC.UnderSpeed * 0.95) {
						pccState = PCCStates.UseCase1;
					}
					break;
			}

			switch (pccState) {
				case PCCStates.UseCase1:
				case PCCStates.UseCase2:
					switch (ADAS.EcoRoll) {
						case EcoRollType.None: break;
						case EcoRollType.WithoutEngineStop:
							if (DataBus.GearboxCtl() != null) {
								DataBus.GearboxCtl().DisengageGearbox = true;
							}
						
							break;
						case EcoRollType.WithEngineStop:
							if (DataBus.GearboxCtl() != null) {
								DataBus.GearboxCtl().DisengageGearbox = true;
							}
							if (DataBus.EngineCtl != null) {
								DataBus.EngineCtl.CombustionEngineOn = false;
							}
							break;
						default: throw new ArgumentOutOfRangeException();
					}

					break;
				case PCCStates.OutsideSegment:
				case PCCStates.WithinSegment:
				case PCCStates.PCCinterrupt:
					if (DataBus.GearboxCtl() != null) {
						DataBus.GearboxCtl().DisengageGearbox = false;
					}

					if (DataBus.EngineCtl != null) {
						DataBus.EngineCtl.CombustionEngineOn = true;
					}
					break;
				default: throw new ArgumentOutOfRangeException();
			}
		}

		private void UpdatePCCState(MeterPerSecond targetVelocity)
		{
			// check if within PCC segment and update state ----------------------------
			var distance = DataBus.MileageCounter.Distance;
			var withinPCCSegment = PCCSegments.Current != null
									&& PCCSegments.Current.StartDistance <= distance
									&& distance <= PCCSegments.Current.EndDistance;

			if (!withinPCCSegment) {
				pccState = PCCStates.OutsideSegment;
				return;
			}
			if (pccState == PCCStates.OutsideSegment) {
				pccState = PCCStates.WithinSegment;
			}
			if (pccState != PCCStates.WithinSegment)
				return;

			// check for PCC usecase 1 -------------------------------------------------
			var endUseCase1 = PCCSegments.Current.EndDistance;
			var endEnergyUseCase1 = PCCSegments.Current.EnergyAtEnd;
			if ((distance + Driver.DriverData.PCC.PreviewDistanceUseCase1).IsSmallerOrEqual(endUseCase1)) {
				endUseCase1 = distance + Driver.DriverData.PCC.PreviewDistanceUseCase1;
				var endCycleEntry = DataBus.DrivingCycleInfo.CycleLookAhead(Driver.DriverData.PCC.PreviewDistanceUseCase1);
				endEnergyUseCase1 = CalculateEnergy(endCycleEntry.Altitude, endCycleEntry.VehicleTargetSpeed, DataBus.VehicleInfo.TotalMass);
			}
			var vehicleSpeed = DataBus.VehicleInfo.VehicleSpeed;
			var coastingForce = CalculateCoastingForce(targetVelocity, vehicleSpeed, PCCSegments.Current.Altitude, endUseCase1);
			var energyCoastingEndUseCase1 = (coastingForce * (endUseCase1 - distance)).Cast<Joule>();
			var currentEnergy = CalculateEnergy(DataBus.DrivingCycleInfo.Altitude, vehicleSpeed, DataBus.VehicleInfo.TotalMass);
			var energyCoastingLow = (coastingForce * (PCCSegments.Current.DistanceAtLowestSpeed - distance)).Cast<Joule>();

			var beforeVLow = distance.IsSmaller(PCCSegments.Current.DistanceAtLowestSpeed);
			var speedSufficient = vehicleSpeed.IsGreaterOrEqual(targetVelocity - Driver.DriverData.PCC.UnderSpeed);
			var currentEnergyHigherThanEndUseCase1 = currentEnergy.IsGreaterOrEqual(endEnergyUseCase1 + energyCoastingEndUseCase1);
			var currentEnergyHigherThanMin = currentEnergy.IsGreaterOrEqual(PCCSegments.Current.EnergyAtLowestSpeed + energyCoastingLow);

			if (beforeVLow
				&& speedSufficient
				&& currentEnergyHigherThanEndUseCase1
				&& currentEnergyHigherThanMin) {
				pccState = PCCStates.UseCase1;
				return;
			}

			// check for PCC use case 2 ------------------------------------------------
			var endUseCase2 = PCCSegments.Current.EndDistance;
			var endEnergyUseCase2 = PCCSegments.Current.EnergyAtEnd;
			if ((distance + Driver.DriverData.PCC.PreviewDistanceUseCase2).IsSmallerOrEqual(endUseCase2)) {
				endUseCase2 = distance + Driver.DriverData.PCC.PreviewDistanceUseCase2;
				var endCycleEntry = DataBus.DrivingCycleInfo.CycleLookAhead(Driver.DriverData.PCC.PreviewDistanceUseCase2);
				endEnergyUseCase2 = CalculateEnergy(endCycleEntry.Altitude, endCycleEntry.VehicleTargetSpeed, DataBus.VehicleInfo.TotalMass);
			}
			var energyCoastingEndUseCase2 = coastingForce * (endUseCase2 - distance);

			var beyondVLow = distance.IsGreaterOrEqual(PCCSegments.Current.DistanceAtLowestSpeed);
			var currentEnergyHigherThanEndUseCase2 = currentEnergy.IsGreaterOrEqual(endEnergyUseCase2 + energyCoastingEndUseCase2);
			var speedSufficientUseCase2 = vehicleSpeed.IsGreaterOrEqual(VectoMath.Max(targetVelocity - Driver.DriverData.PCC.UnderSpeed, Driver.DriverData.PCC.MinSpeed));
			var speedBelowTargetspeed = vehicleSpeed.IsSmallerOrEqual(targetVelocity - 1.KMPHtoMeterPerSecond());

			if (beyondVLow
				&& currentEnergyHigherThanEndUseCase2
				&& speedSufficientUseCase2
				&& speedBelowTargetspeed) {
				pccState = PCCStates.UseCase2;
			}
		}

		private Newton CalculateCoastingForce(MeterPerSecond targetVelocity, MeterPerSecond vehicleSpeed, Meter targetAltitude, Meter targetDistance)
		{
			var dataBus = DataBus;
			var airDrag = DataBus.VehicleInfo.AirDragResistance(vehicleSpeed, targetVelocity);
			var rollResistanceForce = DataBus.VehicleInfo.RollingResistance(dataBus.DrivingCycleInfo.RoadGradient);

			//mk20211008 shouldn't we calculate it the same as in ComputeCoastingDistance?
			//var rollResistanceForce = DataBus.VehicleInfo.RollingResistance(
			//	((targetAltitude - DataBus.DrivingCycleInfo.Altitude) / (targetDistance - DataBus.MileageCounter.Distance))
			//	.Value().SI<Radian>());

			var gearboxLoss = DataBus.GearboxInfo().GearboxLoss();
			var axleLoss = DataBus.AxlegearInfo().AxlegearLoss();
			var emDragLoss = CalculateElectricMotorDragLoss();
			var iceDragLoss = GetICEDragLossPCC(dataBus);

			var totalComponentLossPowers = gearboxLoss + axleLoss + emDragLoss - iceDragLoss;
			var coastingResistanceForce = airDrag.AirdragForce + rollResistanceForce + totalComponentLossPowers / vehicleSpeed;
			return coastingResistanceForce;
		}

		private Watt GetICEDragLossLookAheadCoasting(IDataBus dataBus)
		{
			if (PowertrainArchitecture.IsOneOf(VectoSimulationJobType.SerialHybridVehicle,
					VectoSimulationJobType.IEPC_S, VectoSimulationJobType.FCHV, VectoSimulationJobType.FCHV_IEPC)) {
				return 0.SI<Watt>();
			}
			return DataBus.EngineInfo.EngineDragPower(DataBus.EngineInfo.EngineSpeed);
        }

		private Watt GetICEDragLossPCC(IDataBus dataBus)
		{
			if (PowertrainArchitecture.IsOneOf(VectoSimulationJobType.SerialHybridVehicle,
					VectoSimulationJobType.IEPC_S, VectoSimulationJobType.FCHV, VectoSimulationJobType.FCHV_IEPC)) {
				return 0.SI<Watt>();
			}
			var iceDragLoss = 0.SI<Watt>();
			if (dataBus.GearboxInfo().GearboxType.AutomaticTransmission() &&
				dataBus.GearboxInfo().GearboxType != GearboxType.IHPC) {
				switch (ADAS.EcoRoll) {
					case EcoRollType.None:
						iceDragLoss = DataBus.EngineInfo.EngineDragPower(DataBus.EngineInfo.EngineSpeed);
                        break;
					case EcoRollType.WithoutEngineStop:
						iceDragLoss = ATEcoRollReleaseLockupClutch
							? 0.SI<Watt>()
							: DataBus.EngineInfo.EngineDragPower(DataBus.EngineInfo.EngineSpeed);
						break;
					case EcoRollType.WithEngineStop:
						iceDragLoss = 0.SI<Watt>();
						break;
					default:
						throw new ArgumentOutOfRangeException();
				}
			} else {
				if (ADAS.EcoRoll == EcoRollType.None) {
					iceDragLoss = DataBus.EngineInfo.EngineDragPower(DataBus.EngineInfo.EngineSpeed);
				}
			}

			return iceDragLoss;
		}

		private Joule CalculateEnergy(Meter altitude, MeterPerSecond velocity, Kilogram mass) =>
			mass * Physics.GravityAccelleration * altitude + mass * velocity * velocity / 2;

		private void HandleEcoRoll(Second absTime, MeterPerSecond targetVelocity)
		{
			var dBus = DataBus;
			var vehicleSpeedAboveLowerThreshold = dBus.VehicleInfo.VehicleSpeed >= Driver.DriverData.EcoRoll.MinSpeed;
			var slopeNegative = dBus.DrivingCycleInfo.RoadGradient.IsSmaller(0);
			// potential optimization...
			//if (EcoRollState.State != EcoRollStates.EcoRollOn && !slopeNegative) {
			//	EcoRollState.State = EcoRollStates.EcoRollOff;
			//	return;
			//}
			var forces = dBus.VehicleInfo.SlopeResistance(dBus.DrivingCycleInfo.RoadGradient) + dBus.VehicleInfo.RollingResistance(dBus.DrivingCycleInfo.RoadGradient) +
						dBus.VehicleInfo.AirDragResistance(dBus.VehicleInfo.VehicleSpeed, dBus.VehicleInfo.VehicleSpeed).AirdragForce;

			if (dBus.GearboxInfo().GearboxType.AutomaticTransmission() && ATEcoRollReleaseLockupClutch && dBus.VehicleInfo.VehicleSpeed.IsGreater(0)) {
				// for AT transmissions consider engine drag losses during eco-roll events
				forces -= dBus.EngineInfo.EngineDragPower(dBus.EngineInfo.EngineSpeed) / dBus.VehicleInfo.VehicleSpeed;
				forces += (dBus.GearboxInfo().GearboxLoss() + dBus.AxlegearInfo().AxlegearLoss()) / dBus.VehicleInfo.VehicleSpeed;
			}
			var accelerationWithinLimits = (-forces / dBus.VehicleInfo.TotalMass).IsBetween(
				Driver.DriverData.EcoRoll.AccelerationLowerLimit, Driver.DriverData.EcoRoll.AccelerationUpperLimit);
			var accelerationPedalIdle = EcoRollState.AcceleratorPedalIdle;
			var brakeActive = !EcoRollState.PreviousBrakePower.IsEqual(0);
			var vehcleSpeedBelowMax = dBus.VehicleInfo.VehicleSpeed <=
									(ApplyOverspeed(dBus.DrivingCycleInfo.CycleData.LeftSample.VehicleTargetSpeed) - 2.KMPHtoMeterPerSecond());

			EcoRollState.AllConditionsMet = vehicleSpeedAboveLowerThreshold && vehcleSpeedBelowMax && slopeNegative && accelerationWithinLimits &&
											accelerationPedalIdle && !brakeActive;

			EcoRollState.Gear = dBus.GearboxInfo().Gear;
			switch (EcoRollState.State) {
				case EcoRollStates.EcoRollOff:
					if (EcoRollState.AllConditionsMet) {
						EcoRollState.State = EcoRollStates.PreActivation;
						EcoRollState.StateChangeTstmp = absTime;
					}
					break;
				case EcoRollStates.PreActivation:
					if (!EcoRollState.AllConditionsMet) {
						EcoRollState.State = EcoRollStates.EcoRollOff;
						EcoRollState.StateChangeTstmp = absTime;
						break;
					}

					if (absTime - EcoRollState.StateChangeTstmp > Driver.DriverData.EcoRoll.ActivationPhaseDuration) {
						EcoRollState.State = EcoRollStates.EcoRollOn;
						EcoRollState.StateChangeTstmp = absTime;
					}
					break;
				case EcoRollStates.EcoRollOn:
					var belowTargetSpeed = dBus.VehicleInfo.VehicleSpeed.IsSmaller(targetVelocity - Driver.DriverData.EcoRoll.UnderspeedThreshold);
					if (belowTargetSpeed || brakeActive) {
						EcoRollState.State = EcoRollStates.EcoRollOff;
					}
					break;
				default: throw new ArgumentOutOfRangeException();
			}

			switch (EcoRollState.State) {
				case EcoRollStates.EcoRollOn:
					if (dBus.GearboxCtl() != null) {
						dBus.GearboxCtl().DisengageGearbox = true;
					}
			
					if (ADAS.EcoRoll == EcoRollType.WithEngineStop) {
						dBus.EngineCtl.CombustionEngineOn = false;
					}
					return;
				case EcoRollStates.EcoRollOff:
					if (dBus.GearboxCtl() != null) {
						dBus.GearboxCtl().DisengageGearbox = false;
					} 
					
					if (ADAS.EcoRoll == EcoRollType.WithEngineStop) {
						dBus.EngineCtl.CombustionEngineOn = true;
					}
					return;
			}

			EngineOffTimestamp = null;
			dBus.EngineCtl.CombustionEngineOn = true;
		}


		private void HandleEngineStopStartDuringVehicleStop(Second absTime)
		{
			if (DataBus.DrivingCycleInfo.CycleData.LeftSample.PTOActive != PTOActivity.Inactive) {
				// engine stop start is disabled for stops where the PTO is activated
				return;
			}

			if (VehicleHaltTimestamp == null) {
				VehicleHaltTimestamp = absTime;
			}

			if ((absTime - VehicleHaltTimestamp).IsGreaterOrEqual(
				Driver.DriverData.EngineStopStart.EngineOffStandStillActivationDelay)) {
				if (EngineOffTimestamp == null) {
					EngineOffTimestamp = absTime;
					DataBus.EngineCtl.CombustionEngineOn = false;
				}
			}
			if (EngineOffTimestamp != null &&
				(absTime - EngineOffTimestamp).IsGreaterOrEqual(Driver.DriverData.EngineStopStart.MaxEngineOffTimespan)) {
				DataBus.EngineCtl.CombustionEngineOn = true;
			}
		}

		private void UpdateDrivingAction(Meter currentDistance, Meter ds)
		{
			var nextAction = GetNextDrivingAction(ds);
			if (NextDrivingAction == null) {
				if (nextAction != null) {
					// take the new action
					NextDrivingAction = nextAction;
				}
			} else {
				// update action distance for current 'next action'
				UpdateDistancesForCurrentNextAction();

				SetNextDrivingAction(currentDistance, nextAction);
			}
			Log.Debug("Next Driving Action: {0}", NextDrivingAction);
		}

		private void SetNextDrivingAction(Meter currentDistance, DrivingBehaviorEntry nextAction)
		{
			if (nextAction != null) {
				if (nextAction.HasEqualTrigger(NextDrivingAction)) {
					// if the action changes and the vehicle has not yet exceeded the action distance => update the action
					// otherwise do nothing, NextDrivingAction's action distance has already been updated
					if (nextAction.Action != NextDrivingAction.Action && nextAction.ActionDistance > currentDistance) {
						NextDrivingAction = nextAction;
					}
				} else {
					// hmm, we've got a new action that is closer to what we got before?
					if (nextAction.ActionDistance < NextDrivingAction.ActionDistance) {
						NextDrivingAction = nextAction;
					}
				}
			} else {
				NextDrivingAction = null;
			}
		}

		private void UpdateDistancesForCurrentNextAction()
		{
			if (DataBus.VehicleInfo.VehicleSpeed > NextDrivingAction.NextTargetSpeed) {
				var brakingDistance = Driver.ComputeDecelerationDistance(NextDrivingAction.NextTargetSpeed) + BrakingSafetyMargin;
				switch (NextDrivingAction.Action) {
					case DrivingBehavior.Coasting:

						//var coastingDistance = ComputeCoastingDistance(DataBus.VehicleSpeed, NextDrivingAction.NextTargetSpeed);
						var coastingDistance = ComputeCoastingDistance(DataBus.VehicleInfo.VehicleSpeed, NextDrivingAction.CycleEntry);
						NextDrivingAction.CoastingStartDistance = NextDrivingAction.TriggerDistance - coastingDistance;
						NextDrivingAction.BrakingStartDistance = NextDrivingAction.TriggerDistance - brakingDistance;
						break;
					case DrivingBehavior.Braking:
						NextDrivingAction.BrakingStartDistance = NextDrivingAction.TriggerDistance - brakingDistance;
						NextDrivingAction.CoastingStartDistance = double.MaxValue.SI<Meter>();
						break;
					default: throw new ArgumentOutOfRangeException();
				}
			}
		}

		public virtual MeterPerSecond ApplyOverspeed(MeterPerSecond targetSpeed)
		{
			return (targetSpeed + GetOverspeed()).LimitTo(
					0.KMPHtoMeterPerSecond(), VehicleCategory.IsBus() ? Constants.BusParameters.MaxBusSpeed : 500.KMPHtoMeterPerSecond());

		}

		protected internal MeterPerSecond GetOverspeed()
		{
			return ADAS.PredictiveCruiseControl == PredictiveCruiseControlType.Option_1_2_3 && DataBus.DrivingCycleInfo.CycleData.LeftSample.Highway
				? Driver.DriverData.PCC.OverspeedUseCase3
				: Driver.DriverData.OverSpeed.OverSpeed;
		}

		protected internal DrivingBehaviorEntry GetNextDrivingAction(Meter ds)
		{
			var currentSpeed = DataBus.VehicleInfo.VehicleSpeed;

			var lookaheadDistance =
				(currentSpeed.Value() * 3.6 * Driver.DriverData.LookAheadCoasting.LookAheadDistanceFactor).SI<Meter>();
			var stopDistance = Driver.ComputeDecelerationDistance(0.SI<MeterPerSecond>());
			lookaheadDistance = VectoMath.Max(2 * ds, lookaheadDistance, 1.2 * stopDistance + ds);
			var lookaheadData = DataBus.DrivingCycleInfo.LookAhead(lookaheadDistance);

			Log.Debug("Lookahead distance: {0} @ current speed {1}", lookaheadDistance, currentSpeed);
			var nextActions = new List<DrivingBehaviorEntry>();
			foreach (var entry in lookaheadData) {
				var nextTargetSpeed = IsOverspeedAllowed(entry.VehicleTargetSpeed)
					? ApplyOverspeed(entry.VehicleTargetSpeed)
					: entry.VehicleTargetSpeed;
				if (nextTargetSpeed >= currentSpeed) {
					// acceleration is not relevant
					continue;
				}

				nextActions.Add(GetDrivingBehaviorEntry(nextTargetSpeed, currentSpeed, entry));
			}

			if (!nextActions.Any()) {
				return null;
			}

			var nextBrakingAction = nextActions.OrderBy(x => x.BrakingStartDistance).First();
			var nextCoastingAction = nextActions.OrderBy(x => x.CoastingStartDistance).First();

			return nextBrakingAction.TriggerDistance.IsEqual(nextCoastingAction.TriggerDistance)
				? nextCoastingAction
				: nextBrakingAction;

			// MQ: 27.5.2016 remark: one could set the coasting distance to the closest coasting distance as found above to start coasting a little bit earlier.
		}

		private DrivingBehaviorEntry GetDrivingBehaviorEntry(
			MeterPerSecond nextTargetSpeed, MeterPerSecond currentSpeed,
			DrivingCycleData.DrivingCycleEntry entry)
		{
			var action = DrivingBehavior.Braking;

			var brakingDistance = Driver.ComputeDecelerationDistance(nextTargetSpeed) + BrakingSafetyMargin;
			var coastingDistance = ComputeCoastingDistance(currentSpeed, entry);
			if (!Driver.DriverData.LookAheadCoasting.Enabled || coastingDistance < 0) {
				Log.Debug(
					"adding 'Braking' starting at distance {0}. brakingDistance: {1}, triggerDistance: {2}, nextTargetSpeed: {3}",
					entry.Distance - brakingDistance, brakingDistance, entry.Distance, nextTargetSpeed);
				coastingDistance = brakingDistance;
			} else {
				//var coastingDistance = ComputeCoastingDistance(currentSpeed, nextTargetSpeed);
				if (currentSpeed > Driver.DriverData.LookAheadCoasting.MinSpeed) {
					action = DrivingBehavior.Coasting;

					Log.Debug(
						"adding 'Coasting' starting at distance {0}. coastingDistance: {1}, triggerDistance: {2}, nextTargetSpeed: {3}",
						entry.Distance - coastingDistance, coastingDistance, entry.Distance, nextTargetSpeed);
				} else {
					coastingDistance = -1.SI<Meter>();
				}
			}
			var nextEntry = new DrivingBehaviorEntry {
				Action = action,
				CoastingStartDistance = entry.Distance - coastingDistance,
				BrakingStartDistance = entry.Distance - brakingDistance,
				TriggerDistance = entry.Distance,
				NextTargetSpeed = nextTargetSpeed,
				CycleEntry = entry,
			};
			return nextEntry;
		}

		protected internal virtual Meter ComputeCoastingDistance(MeterPerSecond vehicleSpeed,
			DrivingCycleData.DrivingCycleEntry actionEntry)
		{
			var targetSpeed = actionEntry.VehicleTargetSpeed;
			if (IsOverspeedAllowed(actionEntry.VehicleTargetSpeed)) {
				targetSpeed += Driver.DriverData.OverSpeed.OverSpeed;
			}

			var vehicleMass = DataBus.VehicleInfo.TotalMass + DataBus.WheelsInfo.ReducedMassWheels;
			var targetAltitude = actionEntry.Altitude;
			var vehicleAltitude = DataBus.DrivingCycleInfo.Altitude;

			var kineticEnergyAtTarget = vehicleMass * Physics.GravityAccelleration * targetAltitude
											+ vehicleMass * targetSpeed * targetSpeed / 2;
			var currentKineticEnergy = vehicleMass * Physics.GravityAccelleration * vehicleAltitude
											+ vehicleMass * vehicleSpeed * vehicleSpeed / 2;
			var energyDifference = currentKineticEnergy - kineticEnergyAtTarget;

			var airDrag = DataBus.VehicleInfo.AirDragResistance(vehicleSpeed, targetSpeed);
			var rollingResistanceForce = DataBus.VehicleInfo.RollingResistance(
				((targetAltitude - vehicleAltitude) / (actionEntry.Distance - DataBus.MileageCounter.Distance))
				.Value().SI<Radian>());

			var gearboxLossPower = DataBus.GearboxInfo()?.GearboxLoss() ?? 0.SI<Watt>();
			var axleLossPower = DataBus.AxlegearInfo()?.AxlegearLoss() ?? 0.SI<Watt>();
			var emDragLossPower = CalculateElectricMotorDragLoss();
			var iceDragLossPower = GetICEDragLossLookAheadCoasting(DataBus); //DataBus.EngineInfo?.EngineDragPower(DataBus.EngineInfo.EngineSpeed) ?? 0.SI<Watt>();

			var totalComponentLossPowers = gearboxLossPower + axleLossPower + emDragLossPower - iceDragLossPower;
			var coastingResistanceForce = airDrag.AirdragForce + rollingResistanceForce + totalComponentLossPowers / vehicleSpeed;

			var coastingDecisionFactor = Driver.DriverData.LookAheadCoasting.LookAheadDecisionFactor.Lookup(
				targetSpeed, vehicleSpeed - targetSpeed);
			var coastingDistance = (energyDifference / (coastingDecisionFactor * coastingResistanceForce)).Cast<Meter>();
			return coastingDistance;
		}

		private Watt CalculateElectricMotorDragLoss()
		{
			var sum = 0.SI<Watt>();
			var db = DataBus;
			foreach (var emInfo in db.ElectricMotorsInfo.Where(x => x.Position != PowertrainPosition.GEN))
				sum += emInfo.DragPower(
					db.BatteryInfo.InternalVoltage,
					emInfo.ElectricMotorSpeed, db.GearboxesInfo.First(x => x.AxleNumber == emInfo.AxleNumber).Gear);
			return sum;
		}

		public bool IsOverspeedAllowed(MeterPerSecond velocity, bool prohibitOverspeed = false) =>
			!prohibitOverspeed
			// allow overspeed either if enabled in the driver model, or ADAS PCC option 3 is enabled in the vehicle and we are on a highway
			&& (Driver.DriverData.OverSpeed.Enabled || ADAS.PredictiveCruiseControl == PredictiveCruiseControlType.Option_1_2_3 && DataBus.DrivingCycleInfo.CycleData.LeftSample.Highway)
			&& velocity > Driver.DriverData.OverSpeed.MinSpeed
			&& ApplyOverspeed(velocity) < (DataBus.VehicleInfo.MaxVehicleSpeed ?? 500.KMPHtoMeterPerSecond());
	}

	public struct EcoRoll
	{
		public EcoRollStates State;
		public Second StateChangeTstmp;
		public GearshiftPosition Gear;
		public Watt PreviousBrakePower;
		public bool AcceleratorPedalIdle;
		public bool AllConditionsMet;
	}

	public enum EcoRollStates
	{
		EcoRollOff,
		PreActivation,
		EcoRollOn,
	}

	//=====================================

	public interface IDriverMode
	{
		DefaultDriverStrategy DriverStrategy { get; set; }

		IResponse Request(Second absTime, Meter ds, MeterPerSecond targetVelocity, Radian gradient);

		void ResetMode();
	}

	public abstract class AbstractDriverMode : LoggingObject, IDriverMode
	{
		private IDriverActions _driver;
		private DriverData _driverData;
		private IDataBus _dataBus;

		public DefaultDriverStrategy DriverStrategy { get; set; }

		protected IDriverActions Driver => _driver ?? (_driver = DriverStrategy.Driver);

		protected DriverData DriverData => _driverData ?? (_driverData = Driver.DriverData);

		protected IDataBus DataBus => _dataBus ?? (_dataBus = Driver.DataBus);

		public IResponse Request(Second absTime, Meter ds, MeterPerSecond targetVelocity, Radian gradient)
		{
			var response = DoHandleRequest(absTime, ds, targetVelocity, gradient);

			if (DriverStrategy.NextDrivingAction == null || !(response is ResponseSuccess)) {
				return response;
			}

			// if we accelerate in the current simulation interval the ActionDistance of the next action
			// changes and we might pass the ActionDistance - check again...
			if (response.Driver.Acceleration <= 0) {
				return response;
			}

			// if the speed at the end of the simulation interval is below the next target speed 
			// we are fine (no need to brake right now)
			var v2 = DataBus.VehicleInfo.VehicleSpeed + response.Driver.Acceleration * response.SimulationInterval;
			if (v2 <= DriverStrategy.NextDrivingAction.NextTargetSpeed) {
				return response;
			}

			response = CheckRequestDoesNotExceedNextAction(absTime, ds, targetVelocity, gradient, response, out var newds);

			if (ds.IsEqual(newds, 1e-3.SI<Meter>())) {
				return response;
			}

			if (newds.IsSmallerOrEqual(0, 1e-3)) {
				newds = ds / 2.0;

				//DriverStrategy.CurrentDrivingMode = DefaultDriverStrategy.DrivingMode.DrivingModeBrake;
				//DriverStrategy.BrakeTrigger = DriverStrategy.NextDrivingAction;
			}

			var newOperatingPoint = VectoMath.ComputeTimeInterval(
				DataBus.VehicleInfo.VehicleSpeed, response.Driver.Acceleration, DataBus.MileageCounter.Distance,
				newds);
			if (newOperatingPoint.SimulationInterval.IsSmaller(Constants.SimulationSettings.LowerBoundTimeInterval)) {
				// the next time interval will be too short, this may lead to issues with inertia etc. 
				// instead of accelerating, drive at constant speed.
				response = DoHandleRequest(absTime, ds, DataBus.VehicleInfo.VehicleSpeed, gradient, true);
				return response;
			}

			Log.Debug(
				"Exceeding next ActionDistance at {0}. Reducing max Distance from {2} to {1}",
				DriverStrategy.NextDrivingAction.ActionDistance, newds, ds);
			return new ResponseDrivingCycleDistanceExceeded(this) {
				MaxDistance = newds,
			};
		}

		protected abstract IResponse DoHandleRequest(
			Second absTime, Meter ds, MeterPerSecond targetVelocity, Radian gradient,
			bool prohibitOverspeed = false);

		protected abstract IResponse CheckRequestDoesNotExceedNextAction(
			Second absTime, Meter ds, MeterPerSecond targetVelocity, Radian gradient, IResponse response, out Meter newSimulationDistance);

		public abstract void ResetMode();
	}

	//=====================================

	public class DriverModeDrive : AbstractDriverMode
	{
		protected override IResponse DoHandleRequest(Second absTime, Meter ds, MeterPerSecond targetVelocity, 
			Radian gradient, bool prohibitOverspeed = false)
		{
			var debug = new DebugData();

			Driver.DriverBehavior = DrivingBehavior.Driving;
			var velocity = targetVelocity;
			if (DriverStrategy.IsOverspeedAllowed(targetVelocity, prohibitOverspeed)) {
				velocity = DriverStrategy.ApplyOverspeed(velocity);
			}

			if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission() || (DataBus.ClutchInfo().ClutchClosed(absTime) && DataBus.GearboxInfo().GearEngaged(absTime))) {
				if (DataBus.DrivingCycleInfo.CycleData.LeftSample.PTOActive == PTOActivity.PTOActivityRoadSweeping && targetVelocity < DriverStrategy.PTODriveMinSpeed) {
					velocity = DriverStrategy.PTODriveMinSpeed;
					targetVelocity = velocity;
				}

				for (var i = 0; i < 3; i++) {
					var retVal = HandleRequestEngaged(absTime, ds, targetVelocity, gradient, prohibitOverspeed, 
						velocity, debug);
					if (retVal != null) {
						return retVal;
					}
				}

				throw new VectoException("HandleRequestEngaged found no operating point.");
			}

			var response = HandleRequestDisengaged(absTime, ds, gradient, velocity, debug);
			if (response is ResponseDrivingCycleDistanceExceeded) {
				return response;
			}
			if (!(response is ResponseSuccess) && DataBus.ClutchesInfo.First().ClutchClosed(absTime)) {
				response = HandleRequestEngaged(absTime, ds, targetVelocity, gradient, prohibitOverspeed, velocity, debug);
			}

			return response;
		}

		private IResponse HandleRequestDisengaged(Second absTime, Meter ds, Radian gradient, MeterPerSecond velocity,
			DebugData debug)
		{
			if (DataBus.VehicleInfo.VehicleSpeed.IsSmallerOrEqual(0.SI<MeterPerSecond>())) {
				// the clutch is disengaged, and the vehicle stopped - we can't perform a roll action. wait for the clutch to be engaged
				// todo mk 2016-08-23: is this still needed?
				var remainingShiftTime = Constants.SimulationSettings.TargetTimeInterval;
				while (!DataBus.ClutchesInfo.First().ClutchClosed(absTime + remainingShiftTime)) {
					remainingShiftTime += Constants.SimulationSettings.TargetTimeInterval;
				}

				return new ResponseFailTimeInterval(this) {
					DeltaT = remainingShiftTime,
				};
			}

			var response = Driver.DrivingActionRoll(absTime, ds, velocity, gradient);
			debug.Add("[DMD.HRD-0] ClutchOpen -> Roll", response);
			switch (response) {
				case ResponseUnderload _ when DataBus.ClutchesInfo.First().ClutchClosed(absTime):
					response = HandleRequestEngaged(absTime, ds, velocity, gradient, false, velocity, debug);
					break;
				case ResponseUnderload _ when !DataBus.ClutchesInfo.First().ClutchClosed(absTime):
					response = Driver.DrivingActionBrake(absTime, ds, velocity, gradient, response);
					debug.Add("[DMD.HRD-1] Roll:Underload -> Brake", response);
					break;
				case ResponseSpeedLimitExceeded _:
					response = Driver.DrivingActionBrake(absTime, ds, velocity, gradient);
					debug.Add("[DMD.HRD-2] Roll:SpeedLimitExceeded -> Brake", response);
					break;
			}
			return response;
		}

		private IResponse HandleRequestEngaged(
			Second absTime, Meter ds, MeterPerSecond targetVelocity, Radian gradient,
			bool prohibitOverspeed, MeterPerSecond velocityWithOverspeed, DebugData debug)
		{
			// drive along
			var first = FirstAccelerateOrCoast(absTime, ds, targetVelocity, gradient, prohibitOverspeed, velocityWithOverspeed, debug);

			var second = first;
			switch (first) {
				case ResponseUnderload _:
					if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission() && !DataBus.ClutchesInfo.First().ClutchClosed(absTime)) {
						//TODO mk20210616 the whole statement could be de-nested to switch-pattern matching (with "where") if this first "if" would not be here.
						var debugResponse = Driver.DrivingActionRoll(absTime, ds, velocityWithOverspeed, gradient);
						debug.Add("[DMD.HRE-0] (Underload&Overspeed)->Roll", second);
					}

					if (DataBus.VehicleInfo.VehicleSpeed.IsGreater(0) && DriverStrategy.IsOverspeedAllowed(targetVelocity, prohibitOverspeed)) {
						second = Driver.DrivingActionCoast(absTime, ds, velocityWithOverspeed, gradient);
						debug.Add("[DMD.HRE-1] (Underload&Overspeed)->Coast", second);
						second = HandleCoastAfterUnderloadWithOverspeed(absTime, ds, gradient, velocityWithOverspeed, debug, second);
					} else {
						// overrideAction: in case of hybrids with an AT gearbox after an underload we search for braking power because the torque converter
						// may be in creeping condition (e.g. engine propels but torque converter is below drag. -> engine propells and remaining power is 
						// dissipated in brakes.
						// in order that the hybrid controller still selects a solution where the EM propells as well, the brake action announces the 
						// accelerate action.
						// unfortunately, this causes issues for P1 hybrid configurations with AT gearbox in torque converter gear. If the EM propells, the torque
						// converter cannot find an operating point close to the drag point. therefore, do not announce the different action except for driving off from
						// standstill.
						var gearbox = DataBus.GearboxesInfo.First();
						var overrideAction = gearbox.GearboxType.AutomaticTransmission()
											&& (gearbox.Gear.TorqueConverterLocked.HasValue && !gearbox.Gear.TorqueConverterLocked.Value)
											&& (DataBus.ElectricMotorsInfo.Count(x => x.Position == PowertrainPosition.HybridP1) == 0 || DataBus.VehicleInfo.VehicleStopped)
							? DrivingAction.Accelerate
							: (DrivingAction?)null;
						second = Driver.DrivingActionBrake(absTime, ds, velocityWithOverspeed, gradient,
							overrideAction: overrideAction);
						debug.Add("[DMD.HRE-2] (Underload&!Overspeed)->Brake", second);
					}
					break;
				case ResponseEngineSpeedTooHigh _:
					second = Driver.DrivingActionBrake(absTime, ds, targetVelocity, gradient, first);
					break;
				case ResponseSpeedLimitExceeded _:
					if (DriverStrategy.EcoRollState.State == EcoRollStates.EcoRollOn &&
						DataBus.GearboxInfo().GearboxType.AutomaticTransmission() && DriverStrategy.ATEcoRollReleaseLockupClutch) {
						DriverStrategy.EcoRollState.State = EcoRollStates.EcoRollOff;
						DataBus.GearboxCtl().DisengageGearbox = false;
					}
					second = Driver.DrivingActionBrake(absTime, ds, velocityWithOverspeed, gradient);
					debug.Add("[DMD.HRE-3] SpeedLimitExceeded->Brake", second);
					break;
			}

			if (second == null) {
				return null;
			}

			var third = second;

			switch (second) {
				case ResponseGearShift _:
					third = Driver.DrivingActionRoll(absTime, ds, velocityWithOverspeed, gradient);
					debug.Add("[DMD.HRE-4] second: GearShift -> Roll", third);
					switch (third) {
						case ResponseOverload _:
							third = Driver.DrivingActionCoast(absTime, ds, velocityWithOverspeed, gradient);
							debug.Add("[DMD.HRE-5] third:Overload -> try again Coast", third);
							break;
						case ResponseUnderload _:
							// underload may happen if driver limits acceleration when rolling downhill
							third = Driver.DrivingActionBrake(absTime, ds, velocityWithOverspeed, gradient);
							debug.Add("[DMD.HRE-6] third:Underload -> Brake", third);
							break;
						case ResponseSpeedLimitExceeded _:
							third = Driver.DrivingActionBrake(absTime, ds, velocityWithOverspeed, gradient);
							debug.Add("[DMD.HRE-7] third:SpeedLimitExceeded -> Brake", third);

							if (third is ResponseOverload)
							{
                                third = Driver.DrivingActionAccelerate(absTime, ds, velocityWithOverspeed, gradient);
                                debug.Add("[DMD.HRE-7-1] third:Overload after Brake after Gearshift --> Accelerate", third);
                            }

							break;
					}
					break;
				case ResponseOverload _ when DataBus.VehicleInfo.VehicleSpeed.IsGreater(0):
					third = Driver.DrivingActionCoast(absTime, ds, velocityWithOverspeed, gradient);
					debug.Add("[DMD.HRE-8] second:Overload -> Coast", third);

					switch (third) {
						case ResponseGearShift _:
							third = Driver.DrivingActionCoast(absTime, ds, velocityWithOverspeed, gradient);
							debug.Add("[DMD.HRE-9] third:GearShift -> try again Coast", third);
							break;
						case ResponseSpeedLimitExceeded _:
							if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission() &&
								!DataBus.GearboxInfo().Gear.IsLockedGear()) {
								third = Driver.DrivingActionCoast(absTime, ds, velocityWithOverspeed + 1.KMPHtoMeterPerSecond(), gradient);
								debug.Add("[DMD.HRE-10] third:Overload (AT, Converter gear) -> Coast", third);
							} else {
								third = Driver.DrivingActionBrake(absTime, ds, velocityWithOverspeed, gradient);
								debug.Add("[DMD.HRE-11] third:SpeedLimitExceeded -> Brake", third);
							}

							break;
                        case ResponseOverload _:
                            // for cases with IEPC while first is overspeed, second ist overload due to brake + downshift, third is coast with overload
							// also for case with xEV having to accelerate before stop due to positive gradient
                            if (DataBus.GearboxInfo().GearboxType is GearboxType.APTN) {
                                third = Driver.DrivingActionAccelerate(absTime, ds, velocityWithOverspeed, gradient);
                                debug.Add("[DMD.HRE-12] third:Overload (APTN,IEPC) -> Accelerate", third);
                            }
                            break;
                    }
					break;
			}

			return third;
		}

		private IResponse HandleCoastAfterUnderloadWithOverspeed(Second absTime, Meter ds, Radian gradient, 
			MeterPerSecond velocity, DebugData debug, IResponse second)
		{
			if (second is ResponseUnderload || second is ResponseSpeedLimitExceeded) {
				second = Driver.DrivingActionBrake(absTime, ds, velocity, gradient);
				debug.Add("[DMD.HCAUWO-0] second:(Underload|SpeedLimitExceeded) -> Brake", second);
			}
			if (second is ResponseEngineSpeedTooHigh) {
				second = Driver.DrivingActionBrake(absTime, ds, velocity, gradient, second);
				debug.Add("[DMD.HCAUWO-1] second:(EngineSpeedTooHigh|SpeedLimitExceeded) -> Brake with reduced acceleration", second);
			}
			return second;
		}

		private IResponse FirstAccelerateOrCoast(Second absTime, Meter ds, MeterPerSecond targetVelocity, Radian gradient,
			bool prohibitOverspeed, MeterPerSecond velocityWithOverspeed, DebugData debug)
		{
			
			if (DriverStrategy.pccState == PCCStates.UseCase1 || DriverStrategy.pccState == PCCStates.UseCase2) {
				var response = Driver.DrivingActionCoast(absTime, ds, velocityWithOverspeed, gradient);
				debug.Add("[DMD.FAOC-0] Coast", response);
				if (response is ResponseSuccess) {
					return response;
				}
			}

			var isOverspeedAllowed = DriverStrategy.IsOverspeedAllowed(targetVelocity, prohibitOverspeed);
			var isDrivingWithOverspeed = DataBus.VehicleInfo.VehicleSpeed.IsGreaterOrEqual(targetVelocity);
			if (isOverspeedAllowed && isDrivingWithOverspeed) {
				//we are driving in overspeed (VehicleSpeed >= targetVelocity)

				var response = Driver.DrivingActionCoast(absTime, ds, velocityWithOverspeed, gradient);
				debug.Add("[DMD.FAOC-1] Coast", response);

				if (response is ResponseSuccess
					&& response.Driver.Acceleration < 0 && response.Vehicle.VehicleSpeed <= targetVelocity) {
					//do accelerate action if we would come below targetVelocity due to coasting
					response = Driver.DrivingActionAccelerate(absTime, ds, targetVelocity, gradient);
					debug.Add("[DMD.FAOC-2] Accelerate(Success && Acc<0 && VehSpeed <= targetVelocity)", response);
				}
				if (response is ResponseOverload
					&& DataBus.PowertrainInfo.HasCombustionEngine && !DataBus.EngineInfo.EngineOn) {
					response = Driver.DrivingActionAccelerate(absTime, ds, targetVelocity, gradient);
					debug.Add("[DMD.FAOC-3] Accelerate(Overload && ICE off)", response);
				}
				if (response is ResponseOverload
					&& !DataBus.PowertrainInfo.HasCombustionEngine) {
					response = Driver.DrivingActionAccelerate(absTime, ds, targetVelocity, gradient);
					debug.Add("[DMD.FAOC-4] Accelerate(Overload && BEV)", response);
				}
				if (response is ResponseOverload) {
					response = Driver.DrivingActionAccelerate(absTime, ds, targetVelocity, gradient);
					debug.Add("[DMD.FAOC-5] Accelerate(Overload)", response);
				}
				return response;
			} else {
				//we are not driving in overspeed (VehicleSpeed < targetVelocity)

				if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission() && DataBus.GearboxInfo().DisengageGearbox) {
					var response = Driver.DrivingActionCoast(absTime, ds, velocityWithOverspeed, gradient);
					debug.Add("[DMD.FAOC-6] Coast", response);
					return response;
				} else {
					var response = Driver.DrivingActionAccelerate(absTime, ds, targetVelocity, gradient);
					debug.Add("[DMD.FAOC-7] Accelerate", response);
					return response;
				}
			}
		}

		protected override IResponse CheckRequestDoesNotExceedNextAction(
			Second absTime, Meter ds,
			MeterPerSecond targetVelocity, Radian gradient, IResponse response, out Meter newds)
		{
			var nextAction = DriverStrategy.NextDrivingAction;
			newds = ds;
			if (nextAction == null) {
				return response;
			}

			var v2 = DataBus.VehicleInfo.VehicleSpeed + response.Driver.Acceleration * response.SimulationInterval;
			var newBrakingDistance = Driver.DriverData.AccelerationCurve.ComputeDecelerationDistance(v2,
										nextAction.NextTargetSpeed) + DefaultDriverStrategy.BrakingSafetyMargin;
			switch (DriverStrategy.NextDrivingAction.Action) {
				case DrivingBehavior.Coasting:
					var coastingDistance = DriverStrategy.ComputeCoastingDistance(v2, nextAction.CycleEntry);
					var newActionDistance = coastingDistance;
					var safetyFactor = 4.0;
					if (newBrakingDistance > coastingDistance) {
						newActionDistance = newBrakingDistance;
						safetyFactor = 0.5;
					}

					// if the distance at the end of the simulation interval is smaller than the new ActionDistance
					// we are safe - go ahead...
					if ((DataBus.MileageCounter.Distance + ds).IsSmallerOrEqual(
							nextAction.TriggerDistance - newActionDistance,
							Constants.SimulationSettings.DriverActionDistanceTolerance * safetyFactor) &&
						(DataBus.MileageCounter.Distance + ds).IsSmallerOrEqual(nextAction.TriggerDistance - newBrakingDistance)) {
						return response;
					}

					newds = ds / 2; //EstimateAccelerationDistanceBeforeBrake(response, nextAction) ?? ds;
					break;
				case DrivingBehavior.Braking:
					if ((DataBus.MileageCounter.Distance + ds).IsSmaller(nextAction.TriggerDistance - newBrakingDistance)) {
						return response;
					}

					newds = nextAction.TriggerDistance - newBrakingDistance - DataBus.MileageCounter.Distance -
							Constants.SimulationSettings.DriverActionDistanceTolerance / 2;
					break;
				default: return response;
			}

			return response;
		}

		public override void ResetMode() { }
	}

	//=====================================

	public class DriverModeBrake : AbstractDriverMode
	{
		protected enum BrakingPhase
		{
			Coast,
			Brake
		}

		protected BrakingPhase Phase;
		protected bool RetryDistanceExceeded;

		protected override IResponse DoHandleRequest(
			Second absTime, Meter ds, MeterPerSecond targetVelocity, Radian gradient,
			bool prohibitOverspeed = false)
		{
            //If we have reached the target speed exactly we stop breaking

            //if (DataBus.VehicleInfo.VehicleSpeed.IsSmaller(DriverStrategy.BrakeTrigger.NextTargetSpeed, Constants.SimulationSettings.BrakeTriggerSpeedTolerance)
			if (DataBus.VehicleInfo.VehicleSpeed <= DriverStrategy.BrakeTrigger.NextTargetSpeed
				&& !DataBus.VehicleInfo.VehicleStopped) {
				var retVal = HandleTargetspeedReached(absTime, ds, targetVelocity, gradient);
				for (var i = 0; i < 3 && retVal == null; i++) {
					retVal = HandleTargetspeedReached(absTime, ds, targetVelocity, gradient);
				}

				if (retVal == null) {
					throw new VectoException("Failed to find operating point!");
				}

				return retVal;
			}

			var currentDistance = DataBus.MileageCounter.Distance;

			var brakingDistance = Driver.ComputeDecelerationDistance(DriverStrategy.BrakeTrigger.NextTargetSpeed) +
								DefaultDriverStrategy.BrakingSafetyMargin;
			DriverStrategy.BrakeTrigger.BrakingStartDistance = DriverStrategy.BrakeTrigger.TriggerDistance - brakingDistance;
			if (DriverStrategy.BrakeTrigger.Action == DrivingBehavior.Braking) {
				Phase = BrakingPhase.Brake;
			}
			if (Phase == BrakingPhase.Coast) {
				var resp = CheckSwitchingToBraking(ds, currentDistance);
				if (resp != null) {
					return resp;
				}
			}

			switch (Phase) {
				case BrakingPhase.Coast:
					for (var i = 1; i < 3; i++) {
						var retVal = DoCoast(absTime, ds, targetVelocity, gradient, currentDistance);
						if (retVal != null) {
							return retVal;
						}
					}

					throw new VectoException("No valid operating point found");
				case BrakingPhase.Brake: return DoBrake(absTime, ds, targetVelocity, gradient, brakingDistance, currentDistance);
				default: throw new VectoException("Invalid Phase in DriverModeBrake");
			}
		}

		private IResponse DoBrake(
			Second absTime, Meter ds, MeterPerSecond targetVelocity, Radian gradient,
			Meter brakingDistance, Meter currentDistance)
		{
			IResponse response;
			var debug = new DebugData();

			Log.Debug("Phase: BRAKE. breaking distance: {0} start braking @ {1}", brakingDistance,
				DriverStrategy.BrakeTrigger.BrakingStartDistance);

			if (DriverStrategy.BrakeTrigger.BrakingStartDistance.IsSmaller(
				currentDistance, Constants.SimulationSettings.DriverActionDistanceTolerance / 2)) {
				Log.Info("Expected Braking Deceleration could not be reached! {0}",
					DriverStrategy.BrakeTrigger.BrakingStartDistance - currentDistance);
			}

			Meter targetDistance = null;
			if (DataBus.VehicleInfo.VehicleSpeed < Constants.SimulationSettings.MinVelocityForCoast) {
				targetDistance = DriverStrategy.BrakeTrigger.TriggerDistance;
			}

			if (targetDistance == null && DriverStrategy.BrakeTrigger.NextTargetSpeed.IsEqual(0.SI<MeterPerSecond>())) {
				targetDistance = DriverStrategy.BrakeTrigger.TriggerDistance - DefaultDriverStrategy.BrakingSafetyMargin;
			}

			Driver.DriverBehavior = DrivingBehavior.Braking;

			if (DataBus.VehicleInfo.VehicleSpeed.IsEqual(0) && DriverStrategy.BrakeTrigger.NextTargetSpeed.IsEqual(0)) {
				if (ds.IsEqual(targetDistance - currentDistance, 1e-4.SI<Meter>())) {
					return new ResponseDrivingCycleDistanceExceeded(this) {
						MaxDistance = ds / 2
					};
				}
				var tmpTargetVelocity = Math.Max(0.001.KMPHtoMeterPerSecond().Value(),
					Math.Min(
						1.KMPHtoMeterPerSecond().Value(),
						(ds / 0.1).Value()
					)
				).SI<MeterPerSecond>();
				//var tmpTargetVelocity = 1.KMPHtoMeterPerSecond();
				response = Driver.DrivingActionAccelerate(absTime, ds, tmpTargetVelocity, gradient);
				debug.Add("[DMB-DB-1] Accelerate", response);

				if (response is ResponseUnderload) {
					response = Driver.DrivingActionBrake(absTime, ds, tmpTargetVelocity, gradient, response,
						overrideAction: DrivingAction.Accelerate);
					debug.Add("[DMB-DB-2] Brake", response);
				}
			} else {
				response = Driver.DrivingActionBrake(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed,
					gradient, targetDistance: targetDistance);
				debug.Add("[DMB-DB-3] Brake", response);
			}

			if ((DataBus.GearboxInfo().GearboxType.AutomaticTransmission() || DataBus.HybridControllerInfo != null)
				&& response == null) {
				for (var i = 0; i < 3 && response == null; i++) {
					DataBus.Brakes.BrakePower = 0.SI<Watt>();
					response = Driver.DrivingActionBrake(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed,
						gradient, targetDistance: targetDistance);
					debug.Add($"[DMB-DB-4-{i}] Brake", response);
				}

				if (response == null) {
					throw new VectoException("No valid operating point found");
				}
			}
			switch (response) {
				case ResponseOverload r:
					Log.Info("Brake -> Got OverloadResponse during brake action - desired deceleration could not be reached! response: {0}", r);
					if (!DataBus.ClutchesInfo.First().ClutchClosed(absTime)) {
						Log.Info("Brake -> Overload -> Clutch is open - Trying roll action");
						response = Driver.DrivingActionRoll(absTime, ds, targetVelocity, gradient);
						debug.Add("[DMB-DB-5] Roll", response);
						if (response is ResponseSpeedLimitExceeded) {
							response = Driver.DrivingActionBrake(absTime, ds, targetVelocity, gradient);
							debug.Add("[DMB-DB-6] Brake", response);
						}
                        if (DataBus.ClutchesInfo.First().ClutchClosed(absTime))
                        {
                            response = Driver.DrivingActionCoast(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
                            debug.Add("[DMB-DB-6-1] Coast", response);
                            if (response is ResponseGearShift)
                            {
                                response = Driver.DrivingActionCoast(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
                                debug.Add("[DMB-DB-6-2] Coast", response);
                            }
							if ((response is ResponseOverload) || (response is ResponseDrivingCycleDistanceExceeded))
							{
                                response = Driver.DrivingActionAccelerate(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
                                debug.Add("[DMB-DB-6-3] Accelerate", response);
                            }
                        }
                    } else {
						Log.Info("Brake -> Overload -> Clutch is closed - Trying brake action again");
						DataBus.Brakes.BrakePower = 0.SI<Watt>();
						DataBus.HybridControllerCtl?.RepeatDrivingAction(absTime);
						response = Driver.DrivingActionBrake(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed,
							gradient, targetDistance: targetDistance);
						debug.Add("[DMB-DB-7] Brake", response);
						if (response is ResponseOverload) {
							Log.Info("Brake -> Overload -> 2nd Brake -> Overload -> Trying accelerate action");
							var gear = DataBus.GearboxInfo().Gear;
							if (DataBus.GearboxInfo().GearEngaged(absTime)) {
								response = Driver.DrivingActionAccelerate(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
								debug.Add("[DMB-DB-8] Accelerate", response);
								if (response is ResponseOverload)
								{
									Log.Info("Brake -> Overload --> Accelerate -> Overload -> trying coast action");
									response = Driver.DrivingActionCoast(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
									debug.Add("[DMB-DB-8-1] Coast", response);
								}
							} else {
								response = Driver.DrivingActionRoll(absTime, ds, targetVelocity, gradient);
								debug.Add("[DMB-DB-9] Roll", response);
								if (!(response is ResponseSuccess) && DataBus.HybridControllerCtl != null) {
									response = Driver.DrivingActionRoll(absTime, ds, targetVelocity, gradient);
									debug.Add("[DMB-DB-10] Roll", response);
								}
							}

							switch (response) {
								case ResponseGearShift _:
									Log.Info("Brake -> Overload -> 2nd Brake -> Accelerate or Roll -> Got GearShift response, performing roll action");
									response = Driver.DrivingActionRoll(absTime, ds,
										DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
									debug.Add("[DMB-DB-12] Roll", response);
									break;
								case ResponseUnderload _:
									if (gear.Gear != DataBus.GearboxInfo().Gear.Gear || absTime.IsEqual(DataBus.GearboxInfo().LastDownshift))
                                    {
										// AT Gearbox switched gears, shift losses are no longer applied, try once more...
										response = Driver.DrivingActionAccelerate(absTime, ds,
											DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
										debug.Add("[DMB-DB-13] Accelerate", response);
										if (response is ResponseUnderload)
										{
											Log.Info("Brake -> Overload --> Accelerate -> Gearshift -> Accelerate --> Underload --> Accelerate --> Underload --> trying brake action");
											response = Driver.DrivingActionBrake(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed,
												gradient, targetDistance: targetDistance);
											debug.Add("[DMB-DB-14] Brake", response);
										}
                                        if (response is ResponseOverload && DataBus.GearboxInfo().GearboxType is GearboxType.APTN)
                                        {
                                            Log.Info("Brake -> Overload --> Accelerate -> Gearshift -> Accelerate --> Underload --> Accelerate --> Underload --> Brake -> Overload -> trying coast action");
                                            response = Driver.DrivingActionCoast(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
                                            debug.Add("[DMB-DB-15] Coast", response);
                                        }
                                    }
									break;
							}
						}
					}
					break;
				case ResponseGearShift _:
					Log.Info("Brake -> Got GearShift response, performing roll action + brakes");

					//response = Driver.DrivingActionRoll(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
					DataBus.Brakes.BrakePower = 0.SI<Watt>();
					response = Driver.DrivingActionBrake(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed,
						gradient, targetDistance: targetDistance);
					debug.Add("[DMB-DB-14] Brake", response);
					if (response is ResponseOverload) {
						Log.Info("Brake -> Gearshift -> Overload -> trying roll action (no gear engaged)");
						response = Driver.DrivingActionRoll(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
						debug.Add("[DMB-DB-15] Roll", response);
					}
					break;
			}
			return response;
		}

		private IResponse DoCoast(Second absTime, Meter ds, MeterPerSecond targetVelocity, Radian gradient, Meter currentDistance)
		{
			Driver.DriverBehavior = DrivingBehavior.Coasting;
			var response = DataBus.ClutchesInfo.First().ClutchClosed(absTime)
				? Driver.DrivingActionCoast(absTime, ds, VectoMath.Max(targetVelocity, DataBus.VehicleInfo.VehicleSpeed), gradient)
				: Driver.DrivingActionRoll(absTime, ds, VectoMath.Max(targetVelocity, DataBus.VehicleInfo.VehicleSpeed), gradient);
			switch (response) {
				case ResponseUnderload r:
					// coast would decelerate more than driver's max deceleration => issue brakes to decelerate with driver's max deceleration
					response = Driver.DrivingActionBrake(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient, r);
					if ((DriverStrategy.BrakeTrigger.BrakingStartDistance - currentDistance).IsSmallerOrEqual(Constants.SimulationSettings.DriverActionDistanceTolerance)) {
						Phase = BrakingPhase.Brake;
					}
					break;
				case ResponseOverload _:
					// limiting deceleration while coast may result in an overload => issue brakes to decelerate with driver's max deceleration
					response = DataBus.ClutchesInfo.First().ClutchClosed(absTime)
						? Driver.DrivingActionAccelerate(absTime, ds, targetVelocity, gradient)
						: Driver.DrivingActionRoll(absTime, ds, targetVelocity, gradient);
					//Phase = BrakingPhase.Brake;
					break;
				case ResponseDrivingCycleDistanceExceeded r:
					if (!ds.IsEqual(r.MaxDistance)) {
						// distance has been reduced due to vehicle stop in coast/roll action => use brake action to get exactly to the stop-distance
						// TODO what if no gear is enaged (and we need driveline power to get to the stop-distance?
						response = Driver.DrivingActionBrake(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
					}
					break;
				case ResponseEngineSpeedTooHigh r:
					response = Driver.DrivingActionBrake(absTime, ds, targetVelocity, gradient, r);
					break;
			}

			if (response == null) {
				return null;
			}

			var APTGearShiftCondition = ((DataBus.GearboxInfo().GearboxType is GearboxType.APTN || DataBus.GearboxInfo().GearboxType is GearboxType.ATSerial)
                    && ((DataBus.GearboxInfo().LastDownshift?.IsEqual(absTime) ?? false) || (DataBus.GearboxInfo().LastShift?.IsEqual(absTime) ?? false)));

            // handle the SpeedLimitExceeded Response and Gearshift Response separately in case it occurs in one of the requests in the second try
            for (var i = 0; i < 3 && (response is ResponseGearShift || response is ResponseSpeedLimitExceeded || (response is ResponseOverload && APTGearShiftCondition)); i++) {
				switch (response) {
					case ResponseGearShift _:
						response = Driver.DrivingActionRoll(absTime, ds, targetVelocity, gradient);
						break;
					case ResponseSpeedLimitExceeded _:
						response = Driver.DrivingActionBrake(absTime, ds, DataBus.VehicleInfo.VehicleSpeed, gradient);
						if (response is ResponseOverload && !DataBus.ClutchesInfo.First().ClutchClosed(absTime)) {
							response = Driver.DrivingActionRoll(absTime, ds, DataBus.VehicleInfo.VehicleSpeed, gradient);
						}
						if (response is ResponseGearShift) {
							response = Driver.DrivingActionBrake(absTime, ds, DataBus.VehicleInfo.VehicleSpeed, gradient);
						}
						break;
					case ResponseOverload _:
						// add a condition for APTN/IEPC as ResponseGearShift does not exist for them
						// add a condition for ATSerial/ICE as ResponseGearShift does not exist for them
						response = Driver.DrivingActionAccelerate(absTime, ds, DataBus.VehicleInfo.VehicleSpeed, gradient);
						break;

				}
				APTGearShiftCondition = ((DataBus.GearboxInfo().GearboxType is GearboxType.APTN || DataBus.GearboxInfo().GearboxType is GearboxType.ATSerial)
					&& ((DataBus.GearboxInfo().LastDownshift?.IsEqual(absTime) ?? false) || (DataBus.GearboxInfo().LastShift?.IsEqual(absTime) ?? false)));

            }

			return response;
		}

		private IResponse CheckSwitchingToBraking(Meter ds, Meter currentDistance)
		{
			var nextBrakeAction = DriverStrategy.GetNextDrivingAction(ds);
			if (nextBrakeAction != null &&
				!DriverStrategy.BrakeTrigger.TriggerDistance.IsEqual(nextBrakeAction.TriggerDistance) &&
				nextBrakeAction.BrakingStartDistance.IsSmaller(DriverStrategy.BrakeTrigger.BrakingStartDistance)) {
				DriverStrategy.BrakeTrigger = nextBrakeAction;
				Log.Debug(
					"setting brake trigger to new trigger: trigger distance: {0}, start braking @ {1}",
					nextBrakeAction.TriggerDistance, nextBrakeAction.BrakingStartDistance);
			}

			Log.Debug("start braking @ {0}", DriverStrategy.BrakeTrigger.BrakingStartDistance);
			var remainingDistanceToBrake = DriverStrategy.BrakeTrigger.BrakingStartDistance - currentDistance;
			var estimatedTimeInterval = remainingDistanceToBrake / DataBus.VehicleInfo.VehicleSpeed;
			if (estimatedTimeInterval.IsSmaller(Constants.SimulationSettings.LowerBoundTimeInterval) ||
				currentDistance + Constants.SimulationSettings.DriverActionDistanceTolerance >
				DriverStrategy.BrakeTrigger.BrakingStartDistance) {
				Phase = BrakingPhase.Brake;
				Log.Debug("Switching to BRAKE Phase. currentDistance: {0}", currentDistance);
			} else {
				if ((currentDistance + ds).IsGreater(DriverStrategy.BrakeTrigger.BrakingStartDistance)) {
					return new ResponseDrivingCycleDistanceExceeded(this) {
						MaxDistance = DriverStrategy.BrakeTrigger.BrakingStartDistance - currentDistance
					};
				}
			}

			if (DataBus.VehicleInfo.VehicleSpeed < Constants.SimulationSettings.MinVelocityForCoast) {
				Phase = BrakingPhase.Brake;
				Log.Debug(
					"Switching to BRAKE Phase. currentDistance: {0}  v: {1}", currentDistance,
					DataBus.VehicleInfo.VehicleSpeed);
			}
			return null;
		}

		private IResponse HandleTargetspeedReached(Second absTime, Meter ds, MeterPerSecond targetVelocity, Radian gradient)
		{
			var response = TargetSpeedReachedDriveAlong(absTime, ds, targetVelocity, gradient);

			//var i = 0;
			//do {
			switch (response) {
				case ResponseGearShift _:
					response = Driver.DrivingActionRoll(absTime, ds, targetVelocity, gradient);
					switch (response) {
						case ResponseUnderload r:
							// under-load may happen if driver limits acceleration when rolling downhill
							response = Driver.DrivingActionBrake(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient, r);
							break;
						case ResponseSpeedLimitExceeded _:
							response = Driver.DrivingActionBrake(absTime, ds, DataBus.VehicleInfo.VehicleSpeed, gradient);
							break;
					}
					break;
				case ResponseSpeedLimitExceeded _:
					response = Driver.DrivingActionBrake(absTime, ds, DataBus.VehicleInfo.VehicleSpeed, gradient);
					break;
				case ResponseUnderload r:
					//response = Driver.DrivingActionBrake(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed,
					//	gradient, r);
					response = Driver.DrivingActionBrake(absTime, ds,
						DataBus.VehicleInfo.VehicleSpeed + r.Driver.Acceleration * r.SimulationInterval,
						gradient, DataBus.HybridControllerInfo == null ? r : null);
					if (response != null) {
						switch (response) {
							case ResponseGearShift _:
								DataBus.Brakes.BrakePower = 0.SI<Watt>();
								response = Driver.DrivingActionBrake(absTime, ds,
									DriverStrategy.BrakeTrigger.NextTargetSpeed,
									gradient, DataBus.HybridControllerInfo == null ? r : null);
								if (response is ResponseOverload) {
									response = Driver.DrivingActionRoll(absTime, ds,
										DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
								}
								break;
							case ResponseOverload _:
								DataBus.Brakes.BrakePower = 0.SI<Watt>();
								if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission() || DataBus.ClutchesInfo.First().ClutchClosed(absTime)) {
									if (DataBus.VehicleInfo.VehicleSpeed.IsGreater(0)) {
										response = Driver.DrivingActionAccelerate(absTime, ds,
											DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
									} else {
										if (RetryDistanceExceeded) {
											response = Driver.DrivingActionAccelerate(absTime, ds, targetVelocity, gradient);
										} else {
											RetryDistanceExceeded = true;
											response = new ResponseDrivingCycleDistanceExceeded(this) { MaxDistance = ds / 2 };
										}
									}
								} else {
									response = Driver.DrivingActionRoll(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
								}
								break;
						}
					}
					break;
			}

			//} while (!(response is ResponseSuccess) && i++ < 3);
			return response;
		}

		private IResponse TargetSpeedReachedDriveAlong(
			Second absTime, Meter ds, MeterPerSecond targetVelocity,
			Radian gradient)
		{
			IResponse response;
			if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission() || (DataBus.ClutchesInfo.First().ClutchClosed(absTime) && DataBus.GearboxInfo().GearEngaged(absTime))) {
				if (DataBus.VehicleInfo.VehicleSpeed.IsGreater(0)) {
					response = Driver.DrivingActionAccelerate(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
				} else {
					if (RetryDistanceExceeded) {
						response = Driver.DrivingActionAccelerate(absTime, ds, targetVelocity, gradient);
					} else {
						RetryDistanceExceeded = true;
						response = new ResponseDrivingCycleDistanceExceeded(this) { MaxDistance = ds / 2 };
					}
				}
			} else {
				response = Driver.DrivingActionRoll(absTime, ds, DriverStrategy.BrakeTrigger.NextTargetSpeed, gradient);
			}
			return response;
		}

		protected override IResponse CheckRequestDoesNotExceedNextAction(
			Second absTime, Meter ds,
			MeterPerSecond targetVelocity, Radian gradient, IResponse response, out Meter newds)
		{
			var nextAction = DriverStrategy.BrakeTrigger;
			newds = ds;
			if (nextAction == null) {
				return response;
			}

			switch (nextAction.Action) {
				case DrivingBehavior.Coasting:
					var v2 = DataBus.VehicleInfo.VehicleSpeed + response.Driver.Acceleration * response.SimulationInterval;
					var newBrakingDistance = Driver.DriverData.AccelerationCurve.ComputeDecelerationDistance(
						v2,
						nextAction.NextTargetSpeed);
					if ((DataBus.MileageCounter.Distance + ds).IsSmaller(nextAction.TriggerDistance - newBrakingDistance)) {
						return response;
					}

					newds = nextAction.TriggerDistance - newBrakingDistance - DataBus.MileageCounter.Distance -
							Constants.SimulationSettings.DriverActionDistanceTolerance / 2;
					break;
				default: return response;
			}

			return response;
		}

		public override void ResetMode()
		{
			RetryDistanceExceeded = false;
			Phase = BrakingPhase.Coast;
		}
	}

	//=====================================

	[DebuggerDisplay("ActionDistance: {ActionDistance}, TriggerDistance: {TriggerDistance}, Action: {Action}")]
	public class DrivingBehaviorEntry
	{
		public DrivingBehavior Action;
		public MeterPerSecond NextTargetSpeed;
		public Meter TriggerDistance;

		public Meter ActionDistance => VectoMath.Min(
			CoastingStartDistance ?? double.MaxValue.SI<Meter>(),
			BrakingStartDistance ?? double.MaxValue.SI<Meter>());

		public Meter SelectActionDistance(Meter minDistance) =>
			new[] { BrakingStartDistance, CoastingStartDistance }.OrderBy(x => x.Value()).First(x => x >= minDistance);

		public Meter CoastingStartDistance { get; set; }

		public Meter BrakingStartDistance { get; set; }

		public DrivingCycleData.DrivingCycleEntry CycleEntry;

		public bool HasEqualTrigger(DrivingBehaviorEntry other) =>
			TriggerDistance.IsEqual(other.TriggerDistance) && NextTargetSpeed.IsEqual(other.NextTargetSpeed);

		public override string ToString() =>
			$"action: {Action} @ {CoastingStartDistance} / {BrakingStartDistance}. trigger: {TriggerDistance} targetSpeed: {NextTargetSpeed}";
	}
}
