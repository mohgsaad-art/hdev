using System;
using System.Collections.Generic;
using System.Linq;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Configuration;
using TUGraz.VectoCore.Models.Connector.Ports.Impl;
using TUGraz.VectoCore.Models.Simulation;
using TUGraz.VectoCore.Models.Simulation.Data;
using TUGraz.VectoCore.Models.Simulation.DataBus;
using TUGraz.VectoCore.Models.SimulationComponent.Impl.Auxiliaries;
using TUGraz.VectoCore.OutputData;
using TUGraz.VectoCore.Utils;

// ReSharper disable UseStringInterpolation

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{

    /// <summary>
    /// Container Class for Auxiliaries which are connected to the DCDC system.
    /// </summary>
    public class ElectricAuxiliaries : VectoSimulationComponent, IElectricAuxPort
	{
		private IDictionary<string, Func<IDataBus, Watt>> _auxData = new Dictionary<string, Func<IDataBus, Watt>>();
		private IDictionary<string, string> _auxColumnName = new Dictionary<string, string>();
		private IDictionary<string, Watt> _powerDemands = new Dictionary<string, Watt>();


		private HashSet<string> _ignoredIds = new HashSet<string>() {
			Constants.Auxiliaries.IDs.ENGMode_AUX_MECH_FAN,
			Constants.Auxiliaries.IDs.ENGMode_AUX_MECH_STP,
			Constants.Auxiliaries.IDs.ENGMode_AUX_MECH_BASE,
		};
		#region Implementation of IElectricAuxPort


		public ElectricAuxiliaries(IVehicleContainer container) : base(container, Constants.NOT_IN_AXLE_POWERTRAIN)
		{
			
			VehicleContainer = container;

		}

		


		private IVehicleContainer VehicleContainer { get; set; }

		public Watt Initialize()
		{
			
			foreach (var auxId in _auxData.Keys) {
				var id = $"{auxId}_el";
				if (_auxColumnName.ContainsKey(auxId)) {
					continue;
				}
				_auxColumnName.Add(auxId, id); //use column name as ID
				VehicleContainer.AddAuxiliary(id);
			}
			

			return 0.SI<Watt>();
		}

		public void AddAuxiliary(VectoRunData.AuxData aux)
		{
			if (_ignoredIds.Contains(aux.ID)) {
				Log.Debug(string.Format("{0} ignored in {1}", aux.ID, nameof(ElectricAuxiliaries)));
				return;
			}
		

			if (aux.DemandType == AuxiliaryDemandType.Constant) {
				_auxData.Add(aux.ID, (dataBus) => aux.PowerDemandElectric);
			}else if (aux.DemandType == AuxiliaryDemandType.Dynamic) {
				_auxData.Add(aux.ID, (dataBus) => aux.PowerDemandDataBusFunc(dataBus, false));
			}
		}

		public void AddAuxiliary(IAuxDemand aux)
		{
			if (_ignoredIds.Contains(aux.AuxID))
			{
				Log.Debug(string.Format("{0} ignored in {1}", aux.AuxID, nameof(ElectricAuxiliaries)));
				return;
			}
			_auxData.Add(aux.AuxID, aux.PowerDemand);
		}

		public void AddAuxiliaries(IEnumerable<VectoRunData.AuxData> auxData)
		{
			foreach (var aux in auxData) {
				AddAuxiliary(aux);
			}
		}

		public Watt PowerDemand(Second absTime, Second dt, bool dryRun)
		{

			var auxiliarieIgnoredDuringVehicleStop = new[] {
				Constants.Auxiliaries.IDs.SteeringPump,
			};
			var auxiliariesIgnoredWhenICEIsOff = new[] {
				Constants.Auxiliaries.IDs.Fan
			};
			var sum = 0.SI<Watt>();

			var consideredAuxiliaries = _auxData.AsEnumerable();
			if (DataBus.VehicleInfo.VehicleStopped) {
				consideredAuxiliaries = consideredAuxiliaries?.Where(aux => !auxiliarieIgnoredDuringVehicleStop.Contains(aux.Key));
			}

			if (DataBus.EngineInfo != null && !DataBus.EngineInfo.EngineOn) {
				consideredAuxiliaries = consideredAuxiliaries?.Where(aux => !auxiliariesIgnoredWhenICEIsOff.Contains(aux.Key));
			}

			if (consideredAuxiliaries == null) {
				return sum;
			}

			foreach (var aux in consideredAuxiliaries) {


				var powerDemand = 0.SI<Watt>();

				powerDemand += aux.Value(DataBus);



				if (!dryRun) {
					_powerDemands[aux.Key] = powerDemand;
				}

				sum += powerDemand;
			}

			return sum;
		}

		#endregion

		

		#region Overrides of VectoSimulationComponent

		protected override void DoWriteModalResults(Second time, Second simulationInterval, IModalDataContainer container)
		{
			var sum = 0.SI<Watt>();
            foreach (var aux in _auxData)
            {
				var pd = _powerDemands.GetValueOrZero(aux.Key);
				sum += pd;
				container[_auxColumnName[aux.Key]] = pd;
			}

			container[ModalResultField.P_aux_el] = sum;
		}

		protected override void DoCommitSimulationStep(Second time, Second simulationInterval)
		{
			_powerDemands.Clear();
		}

		#endregion

		protected override bool DoUpdateFrom(object other)
		{
			//if (other is ElectricAuxiliaries eAux) {

			//	var updateableConsumers = this._electricConsumers.OfType<IUpdateable>();
			//	var updateableConsumersSource = d._electricConsumers.OfType<IUpdateable>();
			//	System.Diagnostics.Debug.Assert(updateableConsumers.Count() <= 1
			//									&& updateableConsumersSource.Count() <= 1,
			//		"Only 1 updateable subcomponent supported");








			//	return true;
			//} else {
			//	return false;
			//}
			return false;
		}
	}
}

