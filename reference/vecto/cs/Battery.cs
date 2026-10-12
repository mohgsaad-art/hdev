using System;
using System.Linq;
using TUGraz.VectoCommon.Exceptions;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Configuration;
using TUGraz.VectoCore.Models.Connector.Ports.Impl;
using TUGraz.VectoCore.Models.Simulation;
using TUGraz.VectoCore.Models.Simulation.Data;
using TUGraz.VectoCore.Models.SimulationComponent.Data.ElectricComponents.Battery;
using TUGraz.VectoCore.OutputData;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
    public class Battery : StatefulVectoSimulationComponent<Battery.State>, IElectricEnergyStorage, IElectricEnergyStoragePort, IUpdateable
	{
		protected readonly BatteryData ModelData;

		public Battery(IVehicleContainer container, BatteryData modelData) : base(container, Constants.NOT_IN_AXLE_POWERTRAIN)
		{
			ModelData = modelData;
			CurrentState.PulseDuration = 0.SI<Second>();
			PreviousState.PulseDuration = 0.SI<Second>();
			PreviousState.PowerDemand = 0.SI<Watt>();
		}

		#region Implementation of IBatteryProvider
		public IElectricEnergyStoragePort MainBatteryPort => this;

		#endregion


		#region Implementation of IElectricEnergyStoragePort

		public void Initialize(double initialSoC)
		{
			CurrentState.PulseDuration = 0.SI<Second>();
			PreviousState.PulseDuration = 0.SI<Second>();
			PreviousState.PowerDemand = 0.SI<Watt>();

			if (initialSoC.IsSmaller(ModelData.MinSOC) || initialSoC.IsGreater(ModelData.MaxSOC))
			{
				throw new VectoException("SoC must be between {0} and {1} but was {2}", ModelData.MinSOC, ModelData.MaxSOC, initialSoC);
			}
			PreviousState.StateOfCharge = initialSoC;
		}

		public IRESSResponse Request(Second absTime, Second dt, Watt powerDemand, bool dryRun = false)
		{
			var tPulse = PreviousState.PowerDemand.Sign() == powerDemand.Sign()
				? PreviousState.PulseDuration
				: 0.SI<Second>();
			var maxChargePower = MaxChargePower(dt);
			var maxDischargePower = MaxDischargePower(dt);

			
			if (powerDemand.IsGreater(maxChargePower, Constants.SimulationSettings.InterpolateSearchTolerance) ||
				powerDemand.IsSmaller(maxDischargePower, Constants.SimulationSettings.InterpolateSearchTolerance))
			{
				return PowerDemandExceeded(absTime, dt, powerDemand, maxDischargePower, maxChargePower, tPulse, dryRun);
			}

			
			var internalResistance = ModelData.InternalResistance.Lookup(PreviousState.StateOfCharge, tPulse);
			var current = 0.SI<Ampere>();
			if (!powerDemand.IsEqual(0))
			{
				var R_int = InternalResistance(tPulse);
				double[] solutions;
				if (R_int.IsRelativeEqual(0.SI<Ohm>()))
				{
					//Linear solution, quadratic equation solver would become unstable if a is very close to zero
					solutions = new[] {
						(powerDemand / InternalVoltage).Value()
					};
				}
				else
				{
					solutions = VectoMath.QuadraticEquationSolver(InternalResistance(tPulse).Value(), InternalVoltage.Value(),
						-powerDemand.Value());
				}
				current = SelectSolution(solutions, powerDemand.Value());
			}
			var batteryLoss = current * internalResistance * current;
			var currentCharge = ModelData.Capacity * PreviousState.StateOfCharge;

			if (dryRun) {
				return new RESSDryRunResponse(this) {
					AbsTime = absTime,
					SimulationInterval = dt,
					MaxChargePower = maxChargePower,
					MaxDischargePower = maxDischargePower,
					PowerDemand = powerDemand,
					LossPower = batteryLoss,
					StateOfCharge = (currentCharge + current * dt) / ModelData.Capacity,
					InternalVoltage = InternalVoltage
				};
			}
			CurrentState.SimulationInterval = dt;
			CurrentState.PowerDemand = powerDemand;
			CurrentState.TotalCurrent = current;
			CurrentState.BatteryLoss = batteryLoss;

			var soc = (currentCharge + current * dt) / ModelData.Capacity;
			if (ModelData.ChargeDepletingBattery) {
				soc = PreviousState.StateOfCharge.SI<Scalar>();
			}
			CurrentState.StateOfCharge = soc;
			CurrentState.MaxChargePower = maxChargePower;
			CurrentState.MaxDischargePower = maxDischargePower;
			return new RESSResponseSuccess(this) {
				AbsTime = absTime,
				SimulationInterval = dt,
				MaxChargePower = maxChargePower,
				MaxDischargePower = maxDischargePower,
				PowerDemand = powerDemand,
				LossPower = batteryLoss,
				StateOfCharge = soc,
				InternalVoltage = InternalVoltage
			};
		}

		private Ampere SelectSolution(double[] solutions, double sign)
		{
			var maxCurrent = Math.Sign(sign) < 0
				? ModelData.MaxCurrent.LookupMaxDischargeCurrent(PreviousState.StateOfCharge)
				: ModelData.MaxCurrent.LookupMaxChargeCurrent(PreviousState.StateOfCharge);
			return solutions.Where(x => Math.Sign(sign) == Math.Sign(x) && Math.Abs(x).IsSmallerOrEqual(Math.Abs(maxCurrent.Value()), 1e-3)).Min().SI<Ampere>();
		}

		private IRESSResponse PowerDemandExceeded(Second absTime, Second dt, Watt powerDemand, Watt maxDischargePower,
			Watt maxChargePower, Second tPulse, bool dryRun)
		{
			var maxPower = powerDemand < 0 ? maxDischargePower : maxChargePower;

			var maxChargeCurrent = VectoMath.Min((ModelData.MaxSOC - PreviousState.StateOfCharge) * ModelData.Capacity / dt,
				ModelData.MaxCurrent.LookupMaxChargeCurrent(PreviousState.StateOfCharge));
			var maxDischargeCurrent = VectoMath.Max((ModelData.MinSOC - PreviousState.StateOfCharge) * ModelData.Capacity / dt,
				ModelData.MaxCurrent.LookupMaxDischargeCurrent(PreviousState.StateOfCharge));
			var current = powerDemand < 0 ? maxDischargeCurrent : maxChargeCurrent;

			var batteryLoss = current * ModelData.InternalResistance.Lookup(PreviousState.StateOfCharge, tPulse) * current;

			AbstractRESSResponse response;
			if (dryRun) {
				response = new RESSDryRunResponse(this);
			} else {
				if (powerDemand > maxPower) {
					response = new RESSOverloadResponse(this);
				} else {
					response = new RESSUnderloadResponse(this);
				}
			}
			response.AbsTime = absTime;
			response.SimulationInterval = dt;
			response.MaxChargePower = maxChargePower;
			response.MaxDischargePower = maxDischargePower;
			response.PowerDemand = powerDemand;
			response.LossPower = batteryLoss;
			response.InternalVoltage = InternalVoltage;

			return response;
		}

		#endregion


		#region Overrides of VectoSimulationComponent

		protected override void DoWriteModalResults(Second absTime, Second dt, IModalDataContainer container)
		{
			var cellVoltage = ModelData.SOCMap.Lookup(PreviousState.StateOfCharge);
			var tPulse = PreviousState.PowerDemand.Sign() == CurrentState.PowerDemand.Sign()
				? PreviousState.PulseDuration
				: 0.SI<Second>();
			container[ModalResultField.U0_reess, ModelData.BatteryId] = cellVoltage;
			container[ModalResultField.U_reess_terminal, ModelData.BatteryId] =
				cellVoltage +
				CurrentState.TotalCurrent *
				ModelData.InternalResistance.Lookup(PreviousState.StateOfCharge, tPulse); // adding both terms because pos. current charges the battery!
			container[ModalResultField.I_reess, ModelData.BatteryId] = CurrentState.TotalCurrent;
			container[ModalResultField.REESSStateOfCharge, ModelData.BatteryId] = CurrentState.StateOfCharge.SI();
			container[ModalResultField.P_reess_terminal, ModelData.BatteryId] = CurrentState.PowerDemand;
			container[ModalResultField.P_reess_int, ModelData.BatteryId] = cellVoltage * CurrentState.TotalCurrent;
			container[ModalResultField.P_reess_loss, ModelData.BatteryId] = CurrentState.BatteryLoss;
			container[ModalResultField.P_reess_charge_max, ModelData.BatteryId] = CurrentState.MaxChargePower;
			container[ModalResultField.P_reess_discharge_max, ModelData.BatteryId] = CurrentState.MaxDischargePower;
		}



		protected override void DoCommitSimulationStep(Second time, Second simulationInterval)
		{
			var tPulse = PreviousState.PowerDemand.Sign() == CurrentState.PowerDemand.Sign()
				? PreviousState.PulseDuration
				: 0.SI<Second>();
			CurrentState.PulseDuration = tPulse + simulationInterval;
			//if (ModelData.ChargeSustainingBattery) {
			//	CurrentState.StateOfCharge = PreviousState.StateOfCharge;
			//}
			AdvanceState();
		}

		#endregion


		#region Implementation of IRESSInfo
		
		public Volt InternalVoltage => ModelData.SOCMap.Lookup(PreviousState.StateOfCharge);


		public double StateOfCharge => PreviousState.StateOfCharge;

		public WattSecond StoredEnergy => PreviousState.StateOfCharge * ModelData.Capacity * ModelData.SOCMap.Lookup(PreviousState.StateOfCharge);

		public Watt MaxChargePower(Second dt)
		{
			var maxChargeCurrent = MaxChargeCurrent(dt);
			var tPulse = PreviousState.PowerDemand.Sign() > 0 // keep on charging?
				? PreviousState.PulseDuration
				: 0.SI<Second>();
			return InternalVoltage * maxChargeCurrent +
					maxChargeCurrent * InternalResistance(tPulse) * maxChargeCurrent;
		}

		

		public Watt MaxDischargePower(Second dt)
		{
			var maxDischargeCurrent = MaxDischargeCurrent(dt);
			var cellVoltage = InternalVoltage;
			var tPulse = PreviousState.PowerDemand.Sign() < 0 // keep on discharging?
				? PreviousState.PulseDuration
				: 0.SI<Second>();
			var internalResistance = InternalResistance(tPulse);
			var maxDischargePower = InternalVoltage * maxDischargeCurrent +
									maxDischargeCurrent * internalResistance * maxDischargeCurrent;
			var maxPower = -cellVoltage / (4 * internalResistance) * cellVoltage;
			return VectoMath.Max(maxDischargePower, maxPower);
		}

		public double MinSoC => ModelData.MinSOC;

		public double MaxSoC => ModelData.MaxSOC;

		public Ohm InternalResistance(Second tPulse)
		{
			return ModelData.InternalResistance.Lookup(PreviousState.StateOfCharge, tPulse);
		}

		public AmpereSecond Capacity => ModelData.Capacity;
		
		public Volt NominalVoltage => ModelData.SOCMap.Lookup(0.5);

		public Ampere MaxChargeCurrent(Second dt)
		{
			return VectoMath.Min(
				(ModelData.MaxSOC - PreviousState.StateOfCharge) * ModelData.Capacity / dt,
				ModelData.MaxCurrent.LookupMaxChargeCurrent(PreviousState.StateOfCharge));
		}

		public Ampere MaxDischargeCurrent(Second dt)
		{
			return VectoMath.Max(
				((ModelData.MinSOC - PreviousState.StateOfCharge) * ModelData.Capacity / dt).LimitTo(ModelData.MaxCurrent.LookupMaxDischargeCurrent(PreviousState.StateOfCharge),
					0.SI<Ampere>()), ModelData.MaxCurrent.LookupMaxDischargeCurrent(PreviousState.StateOfCharge));
		}
		//public Ampere MaxCurrent
		//{
		//	get
		//	{
		//		var cellVoltage = ModelData.SOCMap.Lookup(PreviousState.StateOfCharge);
		//		return VectoMath.Max(-ModelData.MaxCurrent, -cellVoltage / (4 * ModelData.InternalResistance.Lookup(PreviousState.StateOfCharge)));
		//	}
		//}

		#endregion

		public class State
		{
			public double StateOfCharge;

			public Second SimulationInterval;

			public Watt PowerDemand;

			public Ampere TotalCurrent;
			public Watt MaxChargePower;
			public Watt MaxDischargePower;
			public Watt BatteryLoss;
			public Second PulseDuration;
			public State Clone() => (State)MemberwiseClone();
		}


		#region Implementation of IUpdateable

		#region Overrides of VectoSimulationComponent

		public override bool UpdateFrom(object other)
		{
			if (DataBus == null) {
				// in case the battery is part of a battery system, the databus is null because we shall not write any data.
				// allow updating the state, erroneous updates are covered by the batterysystem
				return DoUpdateFrom(other);
			}
			return base.UpdateFrom(other);
		}

		#endregion

		protected override bool DoUpdateFrom(object other) {
			if (other is Battery b) {
				PreviousState = b.PreviousState.Clone();
				return true;
			}

			return false;
		}

		#endregion


	}


}