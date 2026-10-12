using System;
using System.Linq;
using TUGraz.VectoCommon.Exceptions;
using TUGraz.VectoCommon.InputData;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Configuration;
using TUGraz.VectoCore.Models.Simulation.Data;
using TUGraz.VectoCore.Models.Simulation.DataBus;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl.Auxiliaries
{
	public interface IAuxDemand
	{
		Watt PowerDemand(IDataBus dataBus);

		string AuxID { get; }
	}

	public class Conditioning : IAuxDemand
	{
		private readonly Watt _electricPowerDemand;
		private readonly IEPTO _epto;
		private readonly Watt _EMConditioning;

		private bool EPTOOn(IDataBus dataBus)
		{
			return _epto?.EPTOOn(dataBus) ?? false;
		}

		#region Implementation of IAuxDemand

		public string AuxID { get; }

		#endregion

		/// <summary>
		/// Initializes a new instance of the <see cref="Conditioning"/> class.
		/// </summary>
		/// <param name="condAuxData">Conditioning auxiliary data for the given vehicle.</param>
		/// <param name="epto">EPTO if the vehicle presents one.</param>
		/// <param name="_emConditioning">For FCHV vehicle the PEV, i.e. EM/Battery, conditioning is required.</param>
		/// <exception cref="VectoException">Thrown if the auxiliary is other than COND or the power demand is not defined.</exception>
		public Conditioning(VectoRunData.AuxData condAuxData, IEPTO epto = null, Watt _emConditioning = null)
		{
			if (condAuxData.ID != Constants.Auxiliaries.IDs.Cond)
			{
				throw new VectoException($"Invalid {nameof(condAuxData)}: ID must be {Constants.Auxiliaries.IDs.Cond}");
			}

			if (condAuxData.PowerDemandElectric == null)
			{
				throw new VectoException($"No electric power demand set for {condAuxData.ID}");
			}

			_electricPowerDemand = condAuxData.PowerDemandElectric;
			_epto = epto;
			AuxID = condAuxData.ID;
			_EMConditioning = _emConditioning;
		}

		public Watt PowerDemand(IDataBus dataBus)
        {
			switch (dataBus.PowertrainInfo.VehicleArchitecture) {
				case VectoSimulationJobType.BatteryElectricVehicle:
				case VectoSimulationJobType.IEPC_E:
				case VectoSimulationJobType.SerialHybridVehicle:
				case VectoSimulationJobType.IEPC_S:
				case VectoSimulationJobType.Multiple_PEV:
				case VectoSimulationJobType.Multiple_SHEV:
					return GetPEV_SHEV_PowerDemand(dataBus);
				case VectoSimulationJobType.FCHV:
				case VectoSimulationJobType.FCHV_IEPC:
				case VectoSimulationJobType.Multiple_FCHV:
					return Get_FCHV_PowerDemand(dataBus);
				case VectoSimulationJobType.ParallelHybridVehicle:
				case VectoSimulationJobType.IHPC:
					return GetP_HEV_PowerDemand(dataBus);
				case VectoSimulationJobType.EngineOnlySimulation:
				case VectoSimulationJobType.ConventionalVehicle:
				default:
					throw new ArgumentOutOfRangeException($"{nameof(dataBus)}");
			}
		}

		public Watt GetPEV_SHEV_PowerDemand(IDataBus dataBus)
		{
			var oneEmOn = dataBus.GetElectricMotors().Any(elInfo => !elInfo.EmOffPrev);
			if (oneEmOn || EPTOOn(dataBus)) {
				return _electricPowerDemand;
			} else {
				return 0.SI<Watt>();
			}
		}

		public Watt Get_FCHV_PowerDemand(IDataBus dataBus)
		{
			var powerDemand = 0.SI<Watt>();
			var oneEmOn = dataBus.GetElectricMotors().Any(elInfo => !elInfo.EmOffPrev);
			if (oneEmOn || EPTOOn(dataBus))
			{
				powerDemand += _EMConditioning;
			}
			
			if(!dataBus.ElectricSystemInfo.FuelCellPower.IsEqual(0) || dataBus.IsTestPowertrain)
			{
				powerDemand += _electricPowerDemand;
			}

			return powerDemand;
		}

		public Watt GetP_HEV_PowerDemand(IDataBus dataBus)
		{
			double xFactor = 0;

			var elInfo = dataBus.GetElectricMotors().Single();
			if (!elInfo.EmOffPrev)
			{
				var iceInfo = dataBus.EngineInfo;
				var emPower = elInfo.ElectricMotorSpeed * elInfo.ElectricMotorTorque;
				var icePower = iceInfo.EngineSpeed * iceInfo.EngineTorque;
				if (!(emPower + icePower).IsEqual(0)) {
					xFactor = emPower.Abs() / (emPower.Abs() + icePower.Abs());
				}
			}

			return _electricPowerDemand * xFactor;
		}
	}


}
