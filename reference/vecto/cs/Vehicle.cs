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
using System.Linq;
using TUGraz.VectoCommon.Exceptions;
using TUGraz.VectoCommon.InputData;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Configuration;
using TUGraz.VectoCore.Models.Connector.Ports;
using TUGraz.VectoCore.Models.Simulation;
using TUGraz.VectoCore.Models.Simulation.Data;
using TUGraz.VectoCore.Models.Simulation.DataBus;
using TUGraz.VectoCore.Models.SimulationComponent.Data;
using TUGraz.VectoCore.OutputData;
using TUGraz.VectoCore.Utils;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
	public class TestPowertrainVehicle : Vehicle, ITestPowertrainVehicle
	{
		public TestPowertrainVehicle(IVehicleContainer container, VehicleData modelData, AirdragData airdrag) : base(
			container, modelData, airdrag, false)
		{
			if (!container.IsTestPowertrain) {
				throw new VectoException("This class shall not be used in a real powertrain!");
            }
		}
	}

    public class Vehicle : StatefulProviderComponent<Vehicle.VehicleState, IDriverDemandOutPort, IFvInPort, IFvOutPort>,
		IVehicle, IMileageCounter, IFvInPort, IDriverDemandOutPort
    {
		internal readonly VehicleData ModelData;

		public readonly AirdragData AirdragData;

		public Vehicle(IVehicleContainer container, VehicleData modelData, AirdragData airdrag) : this(container,
			modelData, airdrag, false)
		{
			if (container.IsTestPowertrain) {
				throw new VectoException(
					"This class shall not be used in a testpowertrain - use the dedicated class instead!");
            }
		}


		protected Vehicle(IVehicleContainer container, VehicleData modelData, AirdragData airdrag, bool dummy) : base(container, Constants.NOT_IN_AXLE_POWERTRAIN)
		{
			ModelData = modelData;
			AirdragData = airdrag;
			//if (AirdragData?.CrossWindCorrectionCurve != null) {
			//	AirdragData.CrossWindCorrectionCurve.SetDataBus(container);
			//}
		}

		public IResponse Initialize(MeterPerSecond vehicleSpeed, Radian roadGradient)
		{
			SetMaxVehicleSpeed();
			var airdrag = AirDragResistance(vehicleSpeed, vehicleSpeed);

            PreviousState = new VehicleState {
				Distance = DataBus.DrivingCycleInfo.CycleStartDistance,
				Velocity = vehicleSpeed,
				RollingResistance = RollingResistance(roadGradient),
				SlopeResistance = SlopeResistance(roadGradient),
				AirDragResistance = airdrag.AirdragForce,
			};
			PreviousState.VehicleTractionForce = PreviousState.RollingResistance
												+ PreviousState.AirDragResistance
												+ PreviousState.SlopeResistance;

			return NextComponent?.Initialize(PreviousState.VehicleTractionForce, vehicleSpeed);
		}

		protected virtual void SetMaxVehicleSpeed()
		{
			if (!DataBus.PowertrainInfo.VehicleArchitecture.IsOneOf(
					VectoSimulationJobType.SerialHybridVehicle, 
					VectoSimulationJobType.Multiple_FCHV,
					VectoSimulationJobType.Multiple_PEV,
					VectoSimulationJobType.Multiple_SHEV) 
				&& DataBus.PowertrainInfo.HasCombustionEngine) 
			{
				if (DataBus.GearboxInfo() == null || 
					DataBus.AxlegearInfo() == null) 
				{	
					throw new VectoException("Powertrain with combustion engine requires gearbox and axlegear!");
					//return;
				}

				var gearbox = DataBus.GearboxInfo();

				var maxDrivetrainSpeed = VectoMath.Min(
					DataBus.EngineInfo.EngineN95hSpeed, 
					gearbox.GetGearData(gearbox.NumGears).MaxSpeed);

				MaxVehicleSpeed = maxDrivetrainSpeed /
					gearbox.GetGearData(gearbox.NumGears).Ratio /
					DataBus.AxlegearInfo().Ratio /
					(DataBus.AngledriveInfo()?.Ratio ?? 1.0) * 
					DataBus.WheelsInfo.DynamicTyreRadius * 0.995;
			}

			if (DataBus.PowertrainInfo.VehicleArchitecture.IsMultiplePowertrains())
			{
				var ems = DataBus.ElectricMotorsInfo.Where(x => x.Position != PowertrainPosition.GEN);

				MaxVehicleSpeed = ems.Select(em => 
				{
					var maxEMSpeed = em.MaxSpeedDt;
					var ratio = 1.0;

					if (em.Position == PowertrainPosition.BatteryElectricE3)
					{
						ratio = DataBus.AxlegearsInfo.First(x => x.AxleNumber == em.AxleNumber).Ratio;
					}

					if (em.Position == PowertrainPosition.BatteryElectricE2 || em.Position == PowertrainPosition.IEPC)
					{
						var gearbox = DataBus.GearboxesInfo.First(x => x.AxleNumber == em.AxleNumber);

						ratio = gearbox.GetGearData(gearbox.NumGears).Ratio *
								(DataBus.AxlegearsInfo.FirstOrDefault(x => x.AxleNumber == em.AxleNumber)?.Ratio ?? 1.0) *
								(DataBus.AngledrivesInfo.FirstOrDefault(x => x.AxleNumber == em.AxleNumber)?.Ratio ?? 1.0);
						
						maxEMSpeed = VectoMath.Min(em.MaxSpeedDt, gearbox.GetGearData(gearbox.NumGears).MaxSpeed);
					}

					return maxEMSpeed / ratio * DataBus.WheelsInfo.DynamicTyreRadius * 0.995;
				}).Min();

				return;
			}

			if (DataBus.PowertrainInfo.HasElectricMotor) {
				var ems = DataBus.ElectricMotorsInfo.Where(x => x.Position != PowertrainPosition.GEN).ToArray();

				var em = ems.First();
				var pos = em.Position;

				if (pos.IsBatteryElectric()) {
					var maxEMSpeed = em.MaxSpeedDt;

					var ratio = 1.0;
					if (pos == PowertrainPosition.BatteryElectricE3) {
						ratio = DataBus.AxlegearsInfo.First().Ratio;
					}

					if (pos == PowertrainPosition.BatteryElectricE2 || pos == PowertrainPosition.IEPC) {
						var gearbox = DataBus.GearboxesInfo.First();

						ratio = gearbox.GetGearData(gearbox.NumGears).Ratio *
								(DataBus.AxlegearsInfo.FirstOrDefault()?.Ratio ?? 1.0) *
								(DataBus.AngledrivesInfo.FirstOrDefault()?.Ratio ?? 1.0);

						maxEMSpeed = VectoMath.Min(
							em.MaxSpeedDt,
							gearbox.GetGearData(gearbox.NumGears).MaxSpeed);
					}
					MaxVehicleSpeed = maxEMSpeed / ratio * DataBus.WheelsInfo.DynamicTyreRadius * 0.995;
				}
			}
		}

		public IResponse Initialize(MeterPerSecond vehicleSpeed, Radian roadGradient, MeterPerSquareSecond startAcceleration)
		{
			//CurrentState.Velocity = vehicleSpeed + startAcceleration * Constants.SimulationSettings.TargetTimeInterval;
			var airdrag = AirDragResistance(vehicleSpeed,
				vehicleSpeed + startAcceleration * Constants.SimulationSettings.TargetTimeInterval);

            var vehicleAccelerationForce = AccelerationForce(startAcceleration)
											+ RollingResistance(roadGradient)
											+ airdrag.AirdragForce
											+ SlopeResistance(roadGradient);

			var retVal = NextComponent.Initialize(vehicleAccelerationForce, vehicleSpeed);
			return retVal;
		}

		public IResponse Request(Second absTime, Second dt, MeterPerSquareSecond acceleration, Radian gradient,
			bool dryRun = false)
		{

			Log.Debug("Vehicle: acceleration: {0}", acceleration);
			CurrentState.SimulationInterval = dt;
			CurrentState.Acceleration = acceleration;
			CurrentState.Velocity = PreviousState.Velocity + acceleration * dt;
			if (CurrentState.Velocity.IsEqual(0.SI<MeterPerSecond>(),
				Constants.SimulationSettings.VehicleSpeedHaltTolerance)) {
				CurrentState.Velocity = 0.SI<MeterPerSecond>();
			}
			CurrentState.Distance = PreviousState.Distance + PreviousState.Velocity * dt + acceleration * dt * dt / 2;

			CurrentState.DriverAcceleration = AccelerationForce(acceleration);
			CurrentState.RollingResistance = (PreviousState.Velocity + CurrentState.Velocity).IsEqual(0, 1e-9) ? 0.SI<Newton>() : RollingResistance(gradient);
			AirDragLossResult? airDragResistance;
			try {
				airDragResistance = AirDragResistance(PreviousState.Velocity, CurrentState.Velocity);
			} catch (VectoException ex) {
				Log.Warn("Exception during calculation of AirDragResistance: absTime: {0}, dist: {1}, v: {2}. {3}", absTime,
					CurrentState.Distance, CurrentState.Velocity, ex);
				airDragResistance = AirDragResistance(VectoMath.Max(0, PreviousState.Velocity),
					VectoMath.Max(0, CurrentState.Velocity));
			}

			CurrentState.AirDragResistance = airDragResistance.Value.AirdragForce;
			CurrentState.EffectiveAirdragArea = airDragResistance.Value.EffectiveAirDragArea;
            CurrentState.SlopeResistance = SlopeResistance(gradient);

			// DriverAcceleration = vehicleTractionForce - RollingResistance - AirDragResistance - SlopeResistance
			CurrentState.VehicleTractionForce = CurrentState.DriverAcceleration
												+ CurrentState.RollingResistance
												+ CurrentState.AirDragResistance
												+ CurrentState.SlopeResistance;

			var retval = NextComponent.Request(absTime, dt, CurrentState.VehicleTractionForce,
				CurrentState.Velocity, dryRun);
			retval.Vehicle.VehicleSpeed = CurrentState.Velocity;
			return retval;
		}

		protected override void DoWriteModalResults(Second time, Second simulationInterval, IModalDataContainer container)
		{
			var averageVelocity = (PreviousState.Velocity + CurrentState.Velocity) / 2.0;

			container[ModalResultField.v_act] = averageVelocity;

			container[ModalResultField.P_veh_inertia] = CurrentState.DriverAcceleration * averageVelocity;
			container[ModalResultField.P_roll] = CurrentState.RollingResistance * averageVelocity;
			container[ModalResultField.P_air] = CurrentState.AirDragResistance * averageVelocity;
			container[ModalResultField.EffectiveAirDragArea] = CurrentState.EffectiveAirdragArea;
			container[ModalResultField.P_slope] = CurrentState.SlopeResistance * averageVelocity;
			container[ModalResultField.P_trac] = CurrentState.VehicleTractionForce * averageVelocity;

			// sanity check: is the vehicle in step with the cycle?
			if (container[ModalResultField.dist] == DBNull.Value) {
				Log.Warn("Distance field is not set!");
			} else {
				var distance = (SI)container[ModalResultField.dist];
                if (!distance.IsEqual(CurrentState.Distance))
                {
                    Log.Warn("Vehicle Distance diverges from Cycle by {0} [m]. Distance: {1}",
                        (distance - CurrentState.Distance).Value(), distance);
                }
            }
		}

		public Newton RollingResistance(Radian gradient)
		{
			var weight = ModelData.TotalVehicleMass;
			var gravity = Physics.GravityAccelleration;
			var rollCoefficient = ModelData.TotalRollResistanceCoefficient;

			var retVal = Math.Cos(gradient.Value()) * weight * gravity * rollCoefficient;
			Log.Debug("RollingResistance: {0}", retVal);
			return retVal;
		}

		protected internal Newton AccelerationForce(MeterPerSquareSecond accelleration)
		{
			var retVal = ModelData.TotalVehicleMass * accelleration;
			Log.Debug("DriverAcceleration: {0}", retVal);
			return retVal;
		}

		public Newton SlopeResistance(Radian gradient)
		{
			var retVal = ModelData.TotalVehicleMass * Physics.GravityAccelleration * Math.Sin(gradient.Value());
			Log.Debug("SlopeResistance: {0}", retVal);
			return retVal;
		}

		public MeterPerSecond MaxVehicleSpeed { get; set; }

		public AirDragLossResult AirDragResistance(MeterPerSecond previousVelocity, MeterPerSecond nextVelocity)
		{
			var vAverage = (previousVelocity + nextVelocity) / 2;
			if (vAverage.IsEqual(0)) {
				return new AirDragLossResult(0.SI<Watt>(), 0.SI<SquareMeter>(), vAverage);
			}
			var result = ComputeAirDragPowerLoss(previousVelocity, nextVelocity);

			Log.Debug("AirDragResistance: {0}", result);
			return result;
		}

		private AirDragLossResult ComputeAirDragPowerLoss(MeterPerSecond v1, MeterPerSecond v2)
		{
			return AirdragData.CrossWindCorrectionCurve.AverageAirDragPowerLoss(DataBus.DrivingCycleInfo.CycleData.LeftSample, v1, v2, ModelData.AirDensity);
		}

		public Meter Distance => PreviousState.Distance;

		public MeterPerSecond VehicleSpeed => PreviousState.Velocity;

		public bool VehicleStopped => PreviousState.Velocity.IsEqual(0.SI<MeterPerSecond>(), 0.01.SI<MeterPerSecond>());

		public Kilogram VehicleMass => ModelData.TotalCurbMass;

		public Kilogram VehicleLoading => ModelData.Loading;

		public Kilogram TotalMass => ModelData.TotalVehicleMass;

		public CubicMeter CargoVolume => ModelData.CargoVolume;

		public class VehicleState
		{
			public Meter Distance = 0.SI<Meter>();
			public Second SimulationInterval = 0.SI<Second>();
			public Newton AirDragResistance = 0.SI<Newton>();
			public Newton DriverAcceleration = 0.SI<Newton>();
			public Newton RollingResistance = 0.SI<Newton>();
			public Newton SlopeResistance = 0.SI<Newton>();
			public Newton VehicleTractionForce = 0.SI<Newton>();
			public MeterPerSecond Velocity = 0.SI<MeterPerSecond>();
			public MeterPerSquareSecond Acceleration = 0.SI<MeterPerSquareSecond>();
			public SquareMeter EffectiveAirdragArea { get; set; }

			public override string ToString() =>
				$"v: {Velocity}  " +
				$"a: {Acceleration}, " +
				$"dt: {SimulationInterval}, " +
				$"driver_acc: {DriverAcceleration}, " +
				$"roll_res: {RollingResistance}, " +
				$"slope_res: {SlopeResistance}, " +
				$"air_drag: {AirDragResistance}, " +
				$"traction force: {VehicleTractionForce}";

			public VehicleState Clone() => (VehicleState)MemberwiseClone();
		}

		#region Implementation of IUpdateable

		protected override bool DoUpdateFrom(object other) {
			if (other is Vehicle v) {
				PreviousState = v.PreviousState.Clone();
				MaxVehicleSpeed = v.MaxVehicleSpeed;
				return true;
			}
			return false;
		}

		#endregion
	}
}