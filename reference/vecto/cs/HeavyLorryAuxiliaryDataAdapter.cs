using System.Collections.Generic;
using System.Linq;
using TUGraz.VectoCommon.Exceptions;
using TUGraz.VectoCommon.InputData;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Configuration;
using TUGraz.VectoCore.Models.BusAuxiliaries;
using TUGraz.VectoCore.Models.Declaration;
using TUGraz.VectoCore.Models.Simulation.Data;

namespace TUGraz.VectoCore.InputData.Reader.DataObjectAdapter.SimulationComponents.AuxiliaryDataAdapter
{
	public class HeavyLorryAuxiliaryDataAdapter : AuxiliaryDataAdapter
	{
		protected internal virtual HashSet<AuxiliaryType> AuxiliaryTypes { get; } = new HashSet<AuxiliaryType>() {
			AuxiliaryType.ElectricSystem,
			AuxiliaryType.HVAC,
			AuxiliaryType.PneumaticSystem,
			AuxiliaryType.Fan,
			AuxiliaryType.SteeringPump
		};
		protected virtual string errorStringVehicleType => "conventional/hybrid";

		#region Overrides of AuxiliaryDataAdapter

		public override AuxiliaryConfig CreateBusAuxiliariesData(Mission mission, IVehicleDeclarationInputData primaryVehicle, VectoRunData runData)
		{
			throw new System.NotImplementedException();
		}

		

		protected override IList<VectoRunData.AuxData> DoCreateAuxiliaryData(
			IAuxiliariesDeclarationInputData auxInputData,
			IBusAuxiliariesDeclarationData busAuxData,
			MissionType mission,
			VehicleClass hdvClass,
			Meter vehicleLength,
			int? numSteeredAxles,
			VectoSimulationJobType jobType, bool batteryOnlyHybridMode)
		{
			var retVal = new List<VectoRunData.AuxData>();

			if (!new HashSet<AuxiliaryType>(auxInputData.Auxiliaries.Select(aux => aux.Type)).SetEquals(AuxiliaryTypes))
			{
				var error = string.Format(
					"In Declaration Mode exactly {0} Auxiliaries must be defined for {2} vehicles: {1}",
					AuxiliaryTypes.Count, string.Join(", ", AuxiliaryTypes.Select(aux => aux.ToString())), errorStringVehicleType);
				Log.Error(error);
				throw new VectoException(error);
			}

			var alternatorEfficiency = DeclarationData.AlternatorEfficiency;
			

			foreach (var auxType in AuxiliaryTypes)
			{
				var auxData = auxInputData.Auxiliaries.FirstOrDefault(a => a.Type == auxType);

				if (auxData == null)
				{
					throw new VectoException("Auxiliary {0} not found.", auxType);
				}

				var aux = new VectoRunData.AuxData
				{
					DemandType = AuxiliaryDemandType.Constant,
					Technology = auxData.Technology,
					MissionType = mission,
				};

				mission = mission.GetNonEMSMissionType();
				switch (auxType)
				{
					case AuxiliaryType.Fan:
						AddFan(mission, hdvClass, jobType, auxData, aux, alternatorEfficiency, retVal);
						break;
					case AuxiliaryType.SteeringPump:
						AddSteeringPumps(mission, hdvClass, numSteeredAxles, jobType, auxData, alternatorEfficiency, aux, retVal, batteryOnlyHybridMode);
						break;
					case AuxiliaryType.HVAC:
						AddHVAC(mission, jobType, hdvClass, aux, auxData, 1/DeclarationData.HVACElectricEfficiencyFactor, retVal, batteryOnlyHybridMode);
						break;
					case AuxiliaryType.PneumaticSystem:
						AddPneumaticSystem(mission, jobType, auxData, alternatorEfficiency, aux,retVal, batteryOnlyHybridMode);
						break;
					case AuxiliaryType.ElectricSystem:
						AddElectricSystem(mission, hdvClass, jobType, aux, auxData, alternatorEfficiency, retVal, batteryOnlyHybridMode);
						break;
					default: continue;
				}
			}

			if (CreateConditioningAux(jobType)) {
				AddConditioning(mission, jobType, retVal, hdvClass);
			}

			return retVal;
		}

		private static void AddConditioning(MissionType mission, VectoSimulationJobType jobType, List<VectoRunData.AuxData> auxDataList, VehicleClass hdv)
		{
			var aux = new VectoRunData.AuxData()
			{
				IsFullyElectric = true,
				MissionType = mission,
				DemandType = AuxiliaryDemandType.Dynamic,
				ID = Constants.Auxiliaries.IDs.Cond,
				ConnectToREESS = true,
				PowerDemandElectric = DeclarationData.Conditioning.LookupPowerDemand(hdv, jobType, mission),
			};

			auxDataList.Add(aux);
		}


		private static void AddElectricSystem(MissionType mission, VehicleClass hdvClass,
			VectoSimulationJobType vectoSimulationJobType,
			VectoRunData.AuxData aux,
			IAuxiliaryDeclarationInputData auxData, double alternatorEfficiency, List<VectoRunData.AuxData> auxDataList,
			bool batteryOnlyHybridMode)
		{
			aux.PowerDemandMech = DeclarationData.ElectricSystem.Lookup(hdvClass, mission, auxData.Technology.FirstOrDefault()).PowerDemand;
			aux.ID = Constants.Auxiliaries.IDs.ElectricSystem;
			aux.PowerDemandElectric = aux.PowerDemandMech * alternatorEfficiency;
			aux.ConnectToREESS = batteryOnlyHybridMode || vectoSimulationJobType.IsOneOf(
				VectoSimulationJobType.BatteryElectricVehicle,
				VectoSimulationJobType.SerialHybridVehicle,
				VectoSimulationJobType.IEPC_E,
				VectoSimulationJobType.IEPC_S,
				VectoSimulationJobType.FCHV,
				VectoSimulationJobType.FCHV_IEPC,
				VectoSimulationJobType.Multiple_FCHV,
				VectoSimulationJobType.Multiple_PEV,
				VectoSimulationJobType.Multiple_SHEV);
			auxDataList.Add(aux);
		}

		private static void AddPneumaticSystem(MissionType mission, VectoSimulationJobType jobType,
			IAuxiliaryDeclarationInputData auxData, double alternatorEfficiency, VectoRunData.AuxData aux,
			List<VectoRunData.AuxData> auxDataList, bool batteryOnlyHybridMode)
		{
			if (!DeclarationData.PneumaticSystem.IsApplicable(jobType,
					auxData.Technology.FirstOrDefault())) {
				throw new VectoException(
					$"Pneumatic system technology'{auxData.Technology.FirstOrDefault()}' is not applicable for '{jobType}'");
			}

			aux.PowerDemandMech = DeclarationData.PneumaticSystem.Lookup(mission, auxData.Technology.FirstOrDefault())
				.PowerDemand;
			aux.ID = Constants.Auxiliaries.IDs.PneumaticSystem;
			aux.IsFullyElectric = DeclarationData.PneumaticSystem.IsFullyElectric(auxData.Technology.FirstOrDefault());
			if (aux.IsFullyElectric) {
				aux.PowerDemandElectric =
					DeclarationData.PneumaticSystem.GetElectricPowerDemand(mission,
						auxData.Technology.FirstOrDefault());
			} else {
				aux.PowerDemandElectric = aux.PowerDemandMech * alternatorEfficiency;
			}

			aux.ConnectToREESS = aux.IsFullyElectric && (batteryOnlyHybridMode || jobType.IsOneOf(
				VectoSimulationJobType.BatteryElectricVehicle, 
				VectoSimulationJobType.SerialHybridVehicle, 
				VectoSimulationJobType.IEPC_E, 
				VectoSimulationJobType.IEPC_S,
				VectoSimulationJobType.ParallelHybridVehicle,
				VectoSimulationJobType.FCHV,
				VectoSimulationJobType.FCHV_IEPC,
				VectoSimulationJobType.Multiple_FCHV,
				VectoSimulationJobType.Multiple_PEV,
				VectoSimulationJobType.Multiple_SHEV));
			auxDataList.Add(aux);
		}

		private static void AddHVAC(MissionType mission, VectoSimulationJobType vectoSimulationJobType,
			VehicleClass hdvClass, VectoRunData.AuxData aux,
			IAuxiliaryDeclarationInputData auxData, double efficiency, List<VectoRunData.AuxData> auxDataList,
			bool batteryOnlyHybridMode)
		{
			aux.PowerDemandMech = DeclarationData.HeatingVentilationAirConditioning.Lookup(
				mission,
				auxData.Technology.FirstOrDefault(), hdvClass).PowerDemand;
			aux.ID = Constants.Auxiliaries.IDs.HeatingVentilationAirCondition;
			aux.PowerDemandElectric = aux.PowerDemandMech * efficiency;

			aux.ConnectToREESS = batteryOnlyHybridMode || vectoSimulationJobType.IsOneOf(
				VectoSimulationJobType.BatteryElectricVehicle,
				VectoSimulationJobType.SerialHybridVehicle,
				VectoSimulationJobType.IEPC_S,
				VectoSimulationJobType.IEPC_E,
				VectoSimulationJobType.FCHV,
				VectoSimulationJobType.FCHV_IEPC,
				VectoSimulationJobType.Multiple_FCHV,
				VectoSimulationJobType.Multiple_PEV,
				VectoSimulationJobType.Multiple_SHEV);
			auxDataList.Add(aux);
			return;
		}

		private static void AddSteeringPumps(MissionType mission, VehicleClass hdvClass, int? numSteeredAxles,
			VectoSimulationJobType jobType, IAuxiliaryDeclarationInputData auxData, double alternatorEfficiency,
			VectoRunData.AuxData aux,
			List<VectoRunData.AuxData> auxDataList, bool batteryOnlyHybridMode)
		{
			

			if (!DeclarationData.SteeringPump.IsApplicable(auxData.Technology, jobType)) {
				throw new VectoException(
					$"At least one steering pump technology of '{string.Join(",", auxData.Technology)}' is not applicable for '{jobType}'");
			}

			if (numSteeredAxles.HasValue && auxData.Technology.Count != numSteeredAxles.Value) {
				throw new VectoException(
					$"Number of steering pump technologies does not match number of steered axles ({numSteeredAxles.Value}, {auxData.Technology.Count})");
			}

			var powerDemand = DeclarationData.SteeringPump.Lookup(mission, hdvClass, auxData.Technology);
			var spMech = new VectoRunData.AuxData
			{
				DemandType = AuxiliaryDemandType.Constant,
				Technology = auxData.Technology.Where(tech => !DeclarationData.SteeringPump.IsFullyElectric(tech))
					.ToList(),
				IsFullyElectric = false,
				ID = Constants.Auxiliaries.IDs.SteeringPump,
				PowerDemandMech = powerDemand.mechanicalPumps,

				MissionType = mission,
			};

			if (powerDemand.electricPumps.IsGreater(0))
			{
				var spElectric = new VectoRunData.AuxData
				{
					DemandType = AuxiliaryDemandType.Constant,
					Technology = auxData.Technology.Where(tech => DeclarationData.SteeringPump.IsFullyElectric(tech))
						.ToList(),
					IsFullyElectric = true,
					ConnectToREESS = true,
					ID = Constants.Auxiliaries.IDs.SteeringPump_el,
					PowerDemandElectric = powerDemand.electricPumps * alternatorEfficiency,
					PowerDemandMech = powerDemand.electricPumps,
					MissionType = mission,
				};
				
				if (jobType.IsOneOf(VectoSimulationJobType.ConventionalVehicle, VectoSimulationJobType.EngineOnlySimulation))
				{
					// For a conventional vehicle the electric steering pump power demand
					// is added to the power demand of the mechanical steering pumps.
					spElectric.ConnectToREESS = false;
					spMech.PowerDemandMech += spElectric.PowerDemandMech;
				}
				else
				{
					// For a vehicle with REESS the electric part of the steering pump power demand
					// is treated as separate component.
					auxDataList.Add(spElectric);
				}
			}
			
			if (spMech.PowerDemandMech.IsGreater(0))
			{
				auxDataList.Add(spMech);
			}
		}

		private static void AddFan(MissionType mission, VehicleClass hdvClass, VectoSimulationJobType jobType,
			IAuxiliaryDeclarationInputData auxData, VectoRunData.AuxData aux, double alternatorEfficiency,
			List<VectoRunData.AuxData> auxDataList)
		{
			if (!DeclarationData.Fan.IsApplicable(hdvClass, jobType, auxData.Technology.FirstOrDefault())) {
				throw new VectoException(
					$"Fan technology '{auxData.Technology.FirstOrDefault()}' is not applicable for '{jobType}'");
			}

			aux.PowerDemandMech = DeclarationData.Fan.LookupPowerDemand(hdvClass, mission, auxData.Technology.FirstOrDefault());
			aux.ID = Constants.Auxiliaries.IDs.Fan;
			aux.IsFullyElectric = DeclarationData.Fan.IsFullyElectric(hdvClass, auxData.Technology.FirstOrDefault());
			aux.PowerDemandElectric = aux.PowerDemandMech * alternatorEfficiency;
			aux.ConnectToREESS = aux.IsFullyElectric && (!jobType.IsOneOf(VectoSimulationJobType.ConventionalVehicle,
				VectoSimulationJobType.EngineOnlySimulation));
			auxDataList.Add(aux);
		}
		#endregion
	}

	public class HeavyLorryPEVAuxiliaryDataAdapter : HeavyLorryAuxiliaryDataAdapter
	{
		protected internal override HashSet<AuxiliaryType> AuxiliaryTypes { get; } = new HashSet<AuxiliaryType>() {
			AuxiliaryType.ElectricSystem,
			AuxiliaryType.HVAC,
			AuxiliaryType.PneumaticSystem,
			AuxiliaryType.SteeringPump
		};

		protected override string errorStringVehicleType => "battery electric";
	}

	public class HeavyLorryFCHVAuxiliaryDataAdapter : HeavyLorryPEVAuxiliaryDataAdapter
	{
		protected override string errorStringVehicleType => "FCHV";
	}
}