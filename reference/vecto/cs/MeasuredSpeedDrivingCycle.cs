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
using System.Linq;
using TUGraz.VectoCommon.Exceptions;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCommon.InputData;
using TUGraz.VectoCore.Configuration;
using TUGraz.VectoCore.Models.Connector.Ports;
using TUGraz.VectoCore.Models.Connector.Ports.Impl;
using TUGraz.VectoCore.Models.Simulation;
using TUGraz.VectoCore.Models.Simulation.Data;
using TUGraz.VectoCore.Models.Simulation.DataBus;
using TUGraz.VectoCore.Models.SimulationComponent.Data;
using TUGraz.VectoCore.OutputData;
using TUGraz.VectoCore.Utils;
using TUGraz.VectoCore.Models.SimulationComponent.Strategies;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
	public interface IMeasuredSpeedDrivingCycle : IDriverDemandInProvider { }

    /// <summary>
    /// Driving Cycle for the Measured Speed Gear driving cycle.
    /// </summary>
    public class MeasuredSpeedDrivingCycle :
		StatefulProviderComponent
			<MeasuredSpeedDrivingCycle.DrivingCycleState, ISimulationOutPort, IDriverDemandInPort, IDriverDemandOutPort>,
		IDriverInfo, IDrivingCycleInfo, IMileageCounter, IDriverDemandInProvider, IDriverDemandInPort, ISimulationOutProvider,
		ISimulationOutPort, IMeasuredSpeedDrivingCycle
	{
		public class DrivingCycleState
		{
			public DrivingCycleState Clone()
			{
				return new DrivingCycleState {
					Distance = Distance,
				};
			}

			public Meter Distance;
			public Meter SimulationDistance;
			public MeterPerSquareSecond Acceleration;
		}

		protected readonly IDrivingCycleData Data;

		protected readonly VectoRunData RunData;

		protected internal readonly DrivingCycleEnumerator CycleIterator;

		protected Second AbsTime { get; set; }

		/// <summary>
		/// Initializes a new instance of the <see cref="PowertrainDrivingCycle"/> class.
		/// </summary>
		/// <param name="container">The container.</param>
		/// <param name="cycle">The cycle.</param>
		public MeasuredSpeedDrivingCycle(IVehicleContainer container, IDrivingCycleData cycle)
			: base(container, Constants.NOT_IN_AXLE_POWERTRAIN)
		{
			Data = cycle;
			CycleIterator = new DrivingCycleEnumerator(cycle);

			PreviousState = new DrivingCycleState {
				Distance = 0.SI<Meter>(),
			};
			CurrentState = PreviousState.Clone();

			AbsTime = Data.Entries.First().Time;

			RunData = container.RunData;
		}

        public IResponse Initialize()
		{
			DeclareInterestForGearShiftEvent();

			var first = Data.Entries.First();

			AbsTime = first.Time;

			var response = NextComponent.Initialize(first.VehicleTargetSpeed, first.RoadGradient);
			if (!(response is ResponseSuccess)) {
				throw new UnexpectedResponseException("MeasuredSpeedDrivingCycle: Couldn't find start gear.", response);
			}

			response.AbsTime = AbsTime;
			return response;
		}

		private void DeclareInterestForGearShiftEvent()
		{
			if (RunData.JobType == VectoSimulationJobType.ParallelHybridVehicle) {
				(DataBus.HybridControllerCtl.Strategy as AbstractHybridStrategy).GearShiftTriggered -= GearShiftTriggered;
                (DataBus.HybridControllerCtl.Strategy as AbstractHybridStrategy).GearShiftTriggered += GearShiftTriggered;
			}
			else if ((RunData.JobType == VectoSimulationJobType.BatteryElectricVehicle) ||
				(RunData.JobType == VectoSimulationJobType.ConventionalVehicle)) {
				
				if (DataBus.GearboxesCtl.Count() > 0) {
					DataBus.GearboxesCtl.First().GearShiftTriggered -= GearShiftTriggered;
					DataBus.GearboxesCtl.First().GearShiftTriggered += GearShiftTriggered;
				}
            }
		}

		private void GearShiftTriggered()
        {
			if (DataBus.GearboxesInfo.First(x => x.AxleNumber == Constants.NOT_IN_AXLE_POWERTRAIN).GearboxType == GearboxType.IHPC) {
				return;
            }

			/* Set driving action to roll, on gear change trigger, in order to replicate distance-based mode driver signals. */

			if (DrivingAction == DrivingAction.Accelerate) {
				DriverBehavior = DrivingBehavior.Driving;	
				DrivingAction = DrivingAction.Roll;
			}
        }

		public IResponse Request(Second absTime, Meter ds)
		{
			Log.Fatal("MeasuredSpeed Cycle can not handle distance request.");
			throw new VectoSimulationException("MeasuredSpeed Cycle can not handle distance request.");
		}

		public virtual IResponse Request(Second absTime, Second dt)
		{
			var debug = new DebugData();

			// cycle finished
			if (CycleIterator.LastEntry && absTime >= CycleIterator.RightSample.Time) {
				return new ResponseCycleFinished(this) { AbsTime = absTime };
			}

			if (CycleIterator.RightSample == null) {
				throw new VectoException("Exceeding cycle!");
			}
			// interval exceeded
			if ((absTime + dt).IsGreater(CycleIterator.RightSample.Time)) {
				return new ResponseFailTimeInterval(this) {
					AbsTime = absTime,
					DeltaT = CycleIterator.RightSample.Time - absTime
				};
			}
			if (Constants.SimulationSettings.MeasuredSpeedTargetTimeInterval.IsEqual(dt)) {
				if ((CycleIterator.RightSample.Time - (absTime + dt)) > 0 && (CycleIterator.RightSample.Time - (absTime + dt)) /
					Constants.SimulationSettings.MeasuredSpeedTargetTimeInterval < 0.5) {
					// the remaining simulation interval would be below 0.5 seconds (i.e., half of MeasuredSpeedTargetTimeInterval)
					// reduce the current simulation interval to extend the remaining interval
					return new ResponseFailTimeInterval(this) {
						AbsTime = absTime,
						DeltaT = (CycleIterator.RightSample.Time - absTime) / 2
					};
				}
			}

			// calc acceleration from speed diff vehicle to cycle
			var targetSpeed = CycleIterator.RightSample.VehicleTargetSpeed;
			if (targetSpeed.IsEqual(0.KMPHtoMeterPerSecond(), 0.5.KMPHtoMeterPerSecond())) {
				targetSpeed = 0.KMPHtoMeterPerSecond();
			}
			var deltaV = targetSpeed - DataBus.VehicleInfo.VehicleSpeed;
			var deltaT = CycleIterator.RightSample.Time - absTime;

			if (DataBus.VehicleInfo.VehicleSpeed.IsSmaller(0)) {
				throw new VectoSimulationException("vehicle velocity is smaller than zero");
			}

			if (deltaT.IsSmaller(0)) {
				throw new VectoSimulationException("deltaT is smaller than zero");
			}

			var acceleration = deltaV / deltaT;
			var gradient = CycleIterator.LeftSample.RoadGradient;
			DriverAcceleration = acceleration;
			
			DetermineDriverAction(absTime);    

			IResponse response;
			var responseCount = 0;
			do {
				response = NextComponent.Request(absTime, dt, acceleration, gradient, false);
				debug.Add("MSDC.R-0", response);

				switch (response) {
					case ResponseGearShift _:
						response = NextComponent.Request(absTime, dt, acceleration, gradient, false);
						break;
					case ResponseUnderload r:
						response = HandleUnderload(absTime, dt, r, gradient, ref acceleration);
						break;
					case ResponseOverload r:
						response = HandleOverload(absTime, dt, r, gradient, ref acceleration);
						break;
					case ResponseEngineSpeedTooHigh r:
						acceleration = SearchAlgorithm.Search(acceleration, r.DeltaEngineSpeed,
							Constants.SimulationSettings.OperatingPointInitialSearchIntervalAccelerating,
							getYValue: result => ((ResponseDryRun)result).DeltaEngineSpeed,
							// ReSharper disable once AccessToModifiedClosure
							evaluateFunction: x => NextComponent.Request(absTime, dt, x, gradient, true),
							criterion: y => ((ResponseDryRun)y).DeltaEngineSpeed.Value(),
							searcher: this);
						Log.Info("Found operating point for driver acceleration. absTime: {0}, dt: {1}, acceleration: {2}, gradient: {3}",
							absTime, dt, acceleration, gradient);
						break;
					case ResponseFailTimeInterval r:
						dt = r.DeltaT;
						break;
					case ResponseSuccess _:
						break;
					default:
						throw new UnexpectedResponseException("MeasuredSpeedDrivingCycle received an unexpected response.", response);
				}

			} while (!(response is ResponseSuccess || response is ResponseFailTimeInterval) && (++responseCount < 10));

			AbsTime = absTime + dt;

			response.SimulationInterval = dt;
			response.Driver.Acceleration = acceleration;
			debug.Add("MSDC.R-1", response);

			CurrentState.SimulationDistance = acceleration / 2 * dt * dt + DataBus.VehicleInfo.VehicleSpeed * dt;
			if (CurrentState.SimulationDistance.IsSmaller(0)) {
				throw new VectoSimulationException(
					"MeasuredSpeed: Simulation Distance must not be negative. Driving Backward is not allowed.");
			}

			CurrentState.Distance = CurrentState.SimulationDistance + PreviousState.Distance;
			CurrentState.Acceleration = acceleration;

			return response;
        }

        private void DetermineDriverAction(Second absTime)
        {
			if (RunData.JobType == VectoSimulationJobType.ParallelHybridVehicle) {
				DetermineDriverActionForPHEVAndConventional(absTime);
			}
			else if (RunData.JobType == VectoSimulationJobType.BatteryElectricVehicle) {
				DetermineDriverActionForBEV(absTime);
            }
			else if (RunData.JobType == VectoSimulationJobType.IEPC_E) {
				DetermineDriverActionForBEV(absTime);
            }
			else if (RunData.JobType == VectoSimulationJobType.ConventionalVehicle) {
				DetermineDriverActionForPHEVAndConventional(absTime);
			}
			else {
				DetermineDriverActionForOther();
            }	
		}

        private void DetermineDriverActionWithoutVelocityDropData(Second absTime)
        { 
			bool gearShiftStarted = DetectGearShift();
			var oldAction = DrivingAction;

			if (DataBus.VehicleInfo.VehicleStopped && DriverAcceleration.IsEqual(0)) {
				DriverBehavior = DrivingBehavior.Halted;
				DrivingAction = DrivingAction.Halt;
			}
			else if ((DriverAcceleration < 0) && (oldAction != DrivingAction.Roll)) {
				DriverBehavior = (gearShiftStarted && (oldAction != DrivingAction.Brake)) ? DrivingBehavior.Driving : DrivingBehavior.Braking;
				DrivingAction = (gearShiftStarted && (oldAction != DrivingAction.Brake)) ? DrivingAction.Roll : DrivingAction.Brake;
            }
			else {
				DriverBehavior = DrivingBehavior.Driving;
				DrivingAction = DataBus.GearboxesInfo.First(x => x.AxleNumber == Constants.NOT_IN_AXLE_POWERTRAIN).GearEngaged(absTime)
					? (gearShiftStarted 
						? DrivingAction.Roll 
						: DrivingAction.Accelerate) 
					: DrivingAction.Roll;
			}
        }

        private void DetermineDriverActionForPHEVAndConventional(Second absTime)
        { 
			if (Data.CycleType == CycleType.MeasuredSpeedGear) {
				DetermineDriverActionWithoutVelocityDropData(absTime);
            }
			else if (Data.CycleType == CycleType.MeasuredSpeed) {
				if (DataBus.GearboxesInfo.First(x => x.AxleNumber == Constants.NOT_IN_AXLE_POWERTRAIN).GearboxType.AutomaticTransmission()) {
					DetermineDriverActionForAutomaticTransmission(absTime);	
				}
				else {
					DetermineDriverActionForManualTransmission(absTime);
				}
			}
		}

        private void DetermineDriverActionForAutomaticTransmission(Second absTime)
		{ 
			if (DataBus.VehicleInfo.VehicleStopped && DriverAcceleration.IsEqual(0)) {
				DriverBehavior = DrivingBehavior.Halted;
				DrivingAction = DrivingAction.Halt;

				DataBus.GearboxesCtl.First().DisengageGearbox = false;
			}
			else if ((DriverAcceleration < 0) && (DrivingAction != DrivingAction.Roll)) {
				DriverBehavior = DrivingBehavior.Braking;
				DrivingAction = DrivingAction.Brake;
            }
			else {
				DriverBehavior = DrivingBehavior.Driving;
				var gearbox = DataBus.GearboxesInfo.First(x => x.AxleNumber == Constants.NOT_IN_AXLE_POWERTRAIN);

				DrivingAction = gearbox.GearEngaged(absTime) || (gearbox.GearboxType == GearboxType.IHPC)
					? DrivingAction.Accelerate 
					: DrivingAction.Roll;

				DataBus.GearboxesCtl.First().DisengageGearbox = false;
			}
		}
		
        private void DetermineDriverActionForBEV(Second absTime)
        { 
			if (DataBus.VehicleInfo.VehicleStopped && DriverAcceleration.IsEqual(0)) {
				DriverBehavior = DrivingBehavior.Halted;
				DrivingAction = DrivingAction.Halt;
			}
			else if ((DriverAcceleration < 0) && (DrivingAction != DrivingAction.Roll)) {
				DriverBehavior = DrivingBehavior.Braking;
				DrivingAction = DrivingAction.Brake;
            }
			else {
				DriverBehavior = DrivingBehavior.Driving;
				DrivingAction = DataBus.GearboxesInfo.First(x => x.AxleNumber == Constants.NOT_IN_AXLE_POWERTRAIN).GearEngaged(absTime) 
					? DrivingAction.Accelerate 
					: DrivingAction.Roll;
			}
        }

		private void DetermineDriverActionForOther()
		{
			DriverBehavior = DriverAcceleration < 0
				? DriverBehavior = DrivingBehavior.Braking
				: DriverBehavior = DrivingBehavior.Driving;

			if (DataBus.VehicleInfo.VehicleStopped && DriverAcceleration.IsEqual(0)) {
				DriverBehavior = DrivingBehavior.Halted;
			}
        }

        private void DetermineDriverActionForManualTransmission(Second absTime)
        {
			if (DataBus.VehicleInfo.VehicleStopped && DriverAcceleration.IsEqual(0)) {
				DrivingAction =  DrivingAction.Halt;
				DriverBehavior = DrivingBehavior.Halted;
				
				DataBus.GearboxesCtl.First().DisengageGearbox = false;
            }
			else {
				if (!AreVelocityDropDataAvailable()) {
					DrivingAction = DrivingAction.Accelerate;
					DriverBehavior = DrivingBehavior.Accelerating;
					return;
				}

				var nextSpeed = CalculateVehicleSpeedAtNextStep(absTime);
				var tolerance = (((DataBus.VehicleInfo.VehicleSpeed + nextSpeed) / 2) * 0.001).Abs();

				if (CycleData.RightSample.VehicleTargetSpeed.IsGreater(nextSpeed, tolerance)) {
					var gearbox = DataBus.GearboxesInfo.First(x => x.AxleNumber == Constants.NOT_IN_AXLE_POWERTRAIN);
					
					DrivingAction = gearbox.GearEngaged(absTime) || (gearbox.GearboxType == GearboxType.IHPC) 
						? DrivingAction.Accelerate 
						: DrivingAction.Roll;

					DriverBehavior = (DrivingAction == DrivingAction.Accelerate) ? DrivingBehavior.Accelerating : DrivingBehavior.Driving;

					DataBus.GearboxesCtl.First().DisengageGearbox = false;
				}
				else if (CycleData.RightSample.VehicleTargetSpeed.IsEqual(nextSpeed, tolerance)) {
					DrivingAction = DrivingAction.Roll;
					DriverBehavior = DrivingBehavior.Driving;

					DataBus.GearboxesCtl.First().DisengageGearbox = true;
				}
				else if (CycleData.RightSample.VehicleTargetSpeed.IsSmaller(nextSpeed, tolerance)) {
					DrivingAction = DrivingAction.Brake;
					DriverBehavior = DrivingBehavior.Braking;

					DataBus.GearboxesCtl.First().DisengageGearbox = false;
				}
			}
        }

		private bool AreVelocityDropDataAvailable()
		{
			return ((DataBus.HybridControllerCtl != null) 
				? DataBus.HybridControllerCtl.Strategy.VelocityDropData
				: DataBus.GearboxesInfo.First(x => x.AxleNumber == Constants.NOT_IN_AXLE_POWERTRAIN).Strategy.VelocityDropData) 
				!= null;
		}

        private MeterPerSecond CalculateVehicleSpeedAtNextStep(Second absTime)
        {
			var gearbox = DataBus.GearboxesInfo.First(x => x.AxleNumber == Constants.NOT_IN_AXLE_POWERTRAIN);

			var velocityDropData = (DataBus.HybridControllerCtl != null) 
				? DataBus.HybridControllerCtl.Strategy.VelocityDropData
				: gearbox.Strategy.VelocityDropData;

			var currentSpeed = DataBus.VehicleInfo.VehicleSpeed;
			var interruptionSpeed = velocityDropData.Interpolate(currentSpeed, RoadGradient ?? 0.SI<Radian>());
			var nextSpeed = interruptionSpeed;

			var deltaTime = CycleData.RightSample.Time - absTime;
			
			if (gearbox.TractionInterruption > deltaTime) {
				//Linear interpolation: currSpeed, interruptionSpeed
				var interruptionTime = absTime + gearbox.TractionInterruption;

				nextSpeed = ((currentSpeed * (interruptionTime - CycleData.RightSample.Time)) + (interruptionSpeed * deltaTime)) 
							/ (interruptionTime - absTime);
            }

			return nextSpeed;
		}
		
		private bool DetectGearShift()
		{
			return (Data.CycleType == CycleType.MeasuredSpeedGear) 
				&& (CycleIterator.LeftSample.Gear > 0) 
				&& (CycleIterator.RightSample.Gear == 0);
        }

		private IResponse HandleUnderload(Second absTime, Second dt, ResponseUnderload r,
			Radian gradient, ref MeterPerSquareSecond acceleration)
		{
			MeterPerSquareSecond acc = acceleration;
			DataBus.Brakes.BrakePower = SearchAlgorithm.Search(DataBus.Brakes.BrakePower, r.Delta, -r.Delta,
				getYValue: result => DataBus.ClutchesInfo.First().ClutchClosed(absTime)
					? ((ResponseDryRun)result).DeltaDragLoad
					: ((ResponseDryRun)result).Gearbox.PowerRequest,
				evaluateFunction: x => {
					DataBus.Brakes.BrakePower = x;
					return NextComponent.Request(absTime, dt, acc, gradient, true);
				},
				criterion: y => DataBus.ClutchesInfo.First().ClutchClosed(absTime)
					? ((ResponseDryRun)y).DeltaDragLoad.Value()
					: ((ResponseDryRun)y).Gearbox.PowerRequest.Value(),
				searcher: this);
			Log.Info(
				"Found operating point for braking. absTime: {0}, dt: {1}, acceleration: {2}, gradient: {3}, BrakePower: {4}",
				absTime, dt, acceleration, gradient, DataBus.Brakes.BrakePower);

			if (DataBus.Brakes.BrakePower.IsSmaller(0)) {
				Log.Info(
					"BrakePower was negative: {4}. Setting to 0 and searching for acceleration operating point. absTime: {0}, dt: {1}, acceleration: {2}, gradient: {3}",
					absTime, dt, acceleration, gradient, DataBus.Brakes.BrakePower);
				DataBus.Brakes.BrakePower = 0.SI<Watt>();
				acceleration = SearchAlgorithm.Search(acceleration, r.Delta,
					Constants.SimulationSettings.OperatingPointInitialSearchIntervalAccelerating,
					getYValue: result => ((ResponseDryRun)result).DeltaFullLoad,
					evaluateFunction: x => NextComponent.Request(absTime, dt, x, gradient, true),
					criterion: y => ((ResponseDryRun)y).DeltaFullLoad.Value(),
					searcher: this);
			}

			var response = HandleEngineStall(absTime, dt, r, gradient, ref acceleration);
			if (response != null) {
				return response;
            }
						
			response = NextComponent.Request(absTime, dt, acceleration, gradient, false);
			return response;
		}

		private IResponse HandleEngineStall(Second absTime, Second dt, ResponseUnderload r,
			Radian gradient, ref MeterPerSquareSecond acceleration)
		{
			if ((RunData.JobType == VectoSimulationJobType.ParallelHybridVehicle)
				&& (DrivingAction == DrivingAction.Brake)
				&& ((r.Engine.EngineSpeed ?? 0.SI<PerSecond>()) < DataBus.EngineInfo.EngineIdleSpeed)
				&& (DataBus.GearboxesInfo.First(x => x.AxleNumber == Constants.NOT_IN_AXLE_POWERTRAIN).Gear.Gear == 1)) {

				DataBus.GearboxesCtl.First().DisengageGearbox = true;

				return NextComponent.Request(absTime, dt, acceleration, gradient, false);
            }

			return null;
        }
		
		private IResponse HandleOverload(Second absTime, Second dt, ResponseOverload r, Radian gradient,
			ref MeterPerSquareSecond acceleration)
		{
			if (DataBus.ClutchesInfo.First().ClutchClosed(absTime)) {
				acceleration = SearchAlgorithm.Search(acceleration, r.Delta,
					Constants.SimulationSettings.OperatingPointInitialSearchIntervalAccelerating,
					getYValue: result => ((ResponseDryRun)result).DeltaFullLoad,
					evaluateFunction: x => NextComponent.Request(absTime, dt, x, gradient, true),
					criterion:
						y => ((ResponseDryRun)y).DeltaFullLoad.Value(),
					searcher: this);
				Log.Info(
					"Found operating point for driver acceleration. absTime: {0}, dt: {1}, acceleration: {2}, gradient: {3}",
					absTime, dt, acceleration, gradient);
			} else {
				var acc = acceleration;
				DataBus.Brakes.BrakePower = SearchAlgorithm.Search(DataBus.Brakes.BrakePower, r.Delta, -r.Delta,
					getYValue: result => DataBus.ClutchesInfo.First().ClutchClosed(absTime)
						? ((ResponseDryRun)result).DeltaDragLoad
						: ((ResponseDryRun)result).Gearbox.PowerRequest,
					evaluateFunction: x => {
						DataBus.Brakes.BrakePower = x;
						return NextComponent.Request(absTime, dt, acc, gradient, true);
					},
					criterion: y => DataBus.ClutchesInfo.First().ClutchClosed(absTime)
						? ((ResponseDryRun)y).DeltaDragLoad.Value()
						: ((ResponseDryRun)y).Gearbox.PowerRequest.Value(),
					searcher: this);
				Log.Info(
					"Found operating point for braking. absTime: {0}, dt: {1}, acceleration: {2}, gradient: {3}, BrakePower: {4}",
					absTime, dt, acceleration, gradient, DataBus.Brakes.BrakePower);

				if (DataBus.Brakes.BrakePower.IsSmaller(0)) {
					Log.Info(
						"BrakePower was negative: {4}. Setting to 0 and searching for acceleration operating point. absTime: {0}, dt: {1}, acceleration: {2}, gradient: {3}",
						absTime, dt, acceleration, gradient, DataBus.Brakes.BrakePower);
					DataBus.Brakes.BrakePower = 0.SI<Watt>();
					acceleration = SearchAlgorithm.Search(acceleration, r.Delta,
						Constants.SimulationSettings.OperatingPointInitialSearchIntervalAccelerating,
						getYValue: result => ((ResponseDryRun)result).DeltaFullLoad,
						evaluateFunction: x => NextComponent.Request(absTime, dt, x, gradient, true),
						criterion: y => ((ResponseDryRun)y).DeltaFullLoad.Value(),
						searcher: this);
				}
			}
			var response = NextComponent.Request(absTime, dt, acceleration, gradient, false);
			return response;
		}

		protected override void DoWriteModalResults(Second time, Second simulationInterval, IModalDataContainer container)
		{
			container[ModalResultField.dist] = CurrentState.Distance;
			container[ModalResultField.simulationDistance] = CurrentState.SimulationDistance;
			container[ModalResultField.v_targ] = CycleIterator.LeftSample.VehicleTargetSpeed;
			container[ModalResultField.grad] = CycleIterator.LeftSample.RoadGradientPercent;
			container[ModalResultField.altitude] = CycleIterator.LeftSample.Altitude;
			container[ModalResultField.Highway] = CycleIterator.LeftSample.Highway ? 1 : 0;
            container[ModalResultField.acc] = CurrentState.Acceleration;

			container.SetDataValue("DriverAction", (int)DrivingAction);
		}

		protected override void DoCommitSimulationStep(Second time, Second simulationInterval)
		{
			if ((CycleIterator.RightSample == null) || AbsTime.IsGreaterOrEqual(CycleIterator.RightSample.Time)) {
				CycleIterator.MoveNext();
			}
			AdvanceState();
		}

		protected override bool DoUpdateFrom(object other) => false;

		public double Progress => AbsTime == null ? 0 : AbsTime.Value() / Data.Entries.Last().Time.Value();

		public CycleData CycleData =>
			new CycleData {
				AbsTime = CycleIterator.LeftSample.Time,
				AbsDistance = null,
				LeftSample = CycleIterator.LeftSample,
				RightSample = CycleIterator.RightSample,
			};

		public bool PTOActive => false;

		public DrivingCycleData.DrivingCycleEntry CycleLookAhead(Meter distance)
		{
			return new DrivingCycleData.DrivingCycleEntry(CycleIterator.RightSample);
			//throw new System.NotImplementedException();
		}

		public Meter Altitude => CycleIterator.LeftSample.Altitude;

		public Radian RoadGradient => CycleIterator.LeftSample.RoadGradient;

		public MeterPerSecond TargetSpeed => CycleIterator.LeftSample.VehicleTargetSpeed;

		public Second StopTime => CycleIterator.LeftSample.StoppingTime;

		public Meter CycleStartDistance => 0.SI<Meter>();

		public IReadOnlyList<DrivingCycleData.DrivingCycleEntry> LookAhead(Meter lookaheadDistance)
		{
			throw new NotImplementedException();
		}

		public IReadOnlyList<DrivingCycleData.DrivingCycleEntry> LookAhead(Second time)
		{
			var retVal = new List<DrivingCycleData.DrivingCycleEntry>();

			var iterator = CycleIterator.Clone();
			do {
				retVal.Add(iterator.RightSample);
			} while (iterator.MoveNext() && iterator.RightSample.Time < AbsTime + time);

			return retVal;
		}

		public SpeedChangeEntry LastTargetspeedChange => null;

        public void FinishSimulation() => Data.Finish();

		public DrivingBehavior DriverBehavior { get; internal set; } = DrivingBehavior.Driving;

		public DrivingAction DrivingAction { get; internal set; } = DrivingAction.Accelerate;

		public MeterPerSquareSecond DriverAcceleration { get; protected set; }

		public PCCStates PCCState => PCCStates.OutsideSegment;

		public MeterPerSecond NextBrakeTriggerSpeed => 0.SI<MeterPerSecond>();
		public MeterPerSecond ApplyOverspeed(MeterPerSecond targetSpeed) => targetSpeed;

		public Meter Distance => CurrentState.Distance;
	}
}