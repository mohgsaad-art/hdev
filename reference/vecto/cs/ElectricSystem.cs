using System.Collections.Generic;
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
	public class TestpowertrainElectricSystem : ElectricSystem, ITestpowertrainElectricSystem
	{
		public TestpowertrainElectricSystem(IVehicleContainer container, BatterySystemData batterySystemData) : base(container,
			batterySystemData, false)
		{
			if (container != null && !container.IsTestPowertrain) {
				throw new VectoException(
                    "TestpowertrainElectricSystem component must not be used in real powertrain - use dedicated component instead");
			}
        }
    }

    public class ElectricSystem : StatefulVectoSimulationComponent<ElectricSystem.State>, IElectricSystem, IElectricAuxConnector,
        IElectricChargerConnector, IBatteryConnector, IUpdateable
    {

        protected readonly List<IElectricAuxPort> Consumers = new List<IElectricAuxPort>();

        public IList<IElectricChargerPort> Charger { get; }

		public IFuelCellPort FuelCell { get; private set; } = null;

        protected IElectricEnergyStorage Battery;
        private readonly BatterySystemData ModelData;

		public ElectricSystem(IVehicleContainer container, BatterySystemData batterySystemData) : this(container,
			batterySystemData, false)
		{
			if (container.IsTestPowertrain) {
				throw new VectoException(
					"ElectricSystem component must not be used in test powertrain - use dedicated component instead");
			}
        }

		protected ElectricSystem(IVehicleContainer container, BatterySystemData batterySystemData, bool dummy) : base(container, Constants.NOT_IN_AXLE_POWERTRAIN)
        {
            Charger = new List<IElectricChargerPort>();
            ModelData = batterySystemData;
        }

        public IElectricSystemResponse Request(Second absTime, Second dt, Watt powerDemand, bool dryRun = false)
        {
            powerDemand = powerDemand ?? 0.SI<Watt>();
			var propellingDemand = VectoMath.Min(powerDemand, 0.SI<Watt>()); //Propelling demand is negative
            var maxFcPower = VectoMath.Max(Battery.MaxChargePower(dt) - propellingDemand, 0.SI<Watt>());

            var auxDemand = Consumers.Sum(x => x.PowerDemand(absTime, dt, dryRun)).DefaultIfNull(0);
            var chargePower = Charger.Count == 0 ? 0.SI<Watt>() : Charger.Sum(x => x.PowerDemand(absTime, dt, powerDemand, auxDemand, dryRun));
			var fcPower = FuelCell?.PowerDemand(absTime, dt, maxFcPower, dryRun) ?? 0.SI<Watt>();

			//How to losses when fuel cell is directly contributing to power demand
			var currentEst = (powerDemand + fcPower) / Battery.InternalVoltage;
            var connectorLoss = currentEst * (ModelData?.ConnectionSystemResistance ?? 0.SI<Ohm>()) * currentEst;
            
			var totalPowerDemand = powerDemand + chargePower + fcPower - auxDemand - connectorLoss;
			var maxBatteryPowerDemand = (FuelCell != null) ? VectoMath.Max(totalPowerDemand, Battery.MaxDischargePower(dt)) : totalPowerDemand;
            var batResponse = Battery.MainBatteryPort.Request(absTime, dt, maxBatteryPowerDemand, dryRun);

            var response = dryRun
                ? (AbstractElectricSystemResponse)new ElectricSystemDryRunResponse(this)
                : new ElectricSystemResponseSuccess(this);

            if (batResponse is RESSOverloadResponse) {
                response = new ElectricSystemOverloadResponse(this);
            }
            if (batResponse is RESSUnderloadResponse) {
                response = new ElectricSystemUnderloadResponse(this);
            }

            if (!dryRun) {
                CurrentState.SetState(powerDemand, auxDemand, chargePower + fcPower, connectorLoss, batResponse.PowerDemand, fcPower);
            }

            var fc = (FuelCell != null) ? (FuelCell as FuelCellSystem) : null;
            response.MaxNominalFCRatedPower = (fc != null) 
                ? (fc.FuelCellStrings.All(x => x.FuelCells.All(y => y.FCSRatedPower != null)) ? fc.FuelCellStrings.Sum(x => x.FuelCells.Sum(y => y.FCSRatedPower)) : null)
                : null;

			response.AbsTime = absTime;
            response.SimulationInterval = dt;
            response.RESSResponse = batResponse;
            response.RESSPowerDemand = totalPowerDemand;
            response.ConnectionSystemResistance = ModelData?.ConnectionSystemResistance ?? 0.SI<Ohm>();
            response.ConsumerPower = powerDemand;
            response.AuxPower = auxDemand;
            response.ChargingPower = chargePower + fcPower;
            return response;
        }

        public Watt ElectricAuxPower => PreviousState.AuxPower;
        public Watt ChargePower => PreviousState.ChargePower;
        public Watt BatteryPower => PreviousState.BatteryPower;
		public Watt ConsumerPower => PreviousState.ConsumerPower;
		public Watt FuelCellPower => PreviousState.FuelCellPower;

        protected override void DoWriteModalResults(Second absTime, Second dt, IModalDataContainer container)
        {
            container[ModalResultField.P_Aux_el_HV] = CurrentState.AuxPower;
            container[ModalResultField.P_ES_Conn_loss] = CurrentState.ConnectorLoss;
            container[ModalResultField.P_terminal_ES] = CurrentState.TotalPowerDemand;
        }

        protected override void DoCommitSimulationStep(Second time, Second simulationInterval)
        {
            AdvanceState();
        }


        #region Implementation of IBatteryChargeProvider

        public void Connect(IElectricChargerPort charger)
        {
            Charger.Add(charger);
        }

        #endregion

		public void Connect(IFuelCellPort fuelCell)
		{
			if (FuelCell != null) {
				throw new VectoException("Fuel cell is already connected to ES");

			}

			FuelCell = fuelCell;
		}


        #region Implementation of IBatteryAuxOutProvider

        public void Connect(IElectricAuxPort aux)
        {
            if (Consumers.Contains(aux)) { return; }
            Consumers.Add(aux);
        }

        #endregion

        #region Implementation of IBatteryConnector

        public void Connect(IElectricEnergyStorage battery)
        {
            if (Battery != null) {
                throw new VectoException("Battery is already connected!");
            }
            Battery = battery;
        }

        #endregion

        #region Implementation of IRESSInfo

        public Volt InternalCellVoltage => Battery.InternalVoltage;

        public double StateOfCharge => Battery.StateOfCharge;

        public Watt MaxChargePower(Second dt)
        {
            return Battery.MaxChargePower(dt);
        }

        public Watt MaxDischargePower(Second dt)
        {
            return Battery.MaxDischargePower(dt);
        }


        #endregion

        public class State
        {
            public Watt AuxPower = 0.SI<Watt>();
            public Watt ChargePower = 0.SI<Watt>();
            public Watt ConsumerPower = 0.SI<Watt>();
            public Watt BatteryPower = 0.SI<Watt>();
            public Watt ConnectorLoss = 0.SI<Watt>();
			public Watt FuelCellPower = 0.SI<Watt>();

            public void SetState(Watt powerDemand, Watt auxDemand, Watt chargePower, Watt connectorLoss,
                Watt batteryPower, Watt fuelCellPower)
            {
                AuxPower = auxDemand;
                ChargePower = chargePower;
                ConsumerPower = powerDemand;
                BatteryPower = batteryPower;
                ConnectorLoss = connectorLoss;
				FuelCellPower = fuelCellPower;
            }

            public Watt TotalPowerDemand => ConsumerPower + ChargePower - AuxPower;

            public State Clone() => (State)MemberwiseClone();
        }

        #region Implementation of IUpdateable

        protected override bool DoUpdateFrom(object other)
        {
            if (other is ElectricSystem s) {
                PreviousState = s.PreviousState.Clone();
                return true;
            }

            return false;
        }

        #endregion
    }
}