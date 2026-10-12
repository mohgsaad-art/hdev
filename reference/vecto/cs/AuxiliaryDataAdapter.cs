using System.Collections.Generic;
using TUGraz.VectoCommon.InputData;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.InputData.Reader.DataObjectAdapter.SimulationComponents.Interfaces;
using TUGraz.VectoCore.Models.BusAuxiliaries;
using TUGraz.VectoCore.Models.Declaration;
using TUGraz.VectoCore.Models.Simulation.Data;

namespace TUGraz.VectoCore.InputData.Reader.DataObjectAdapter.SimulationComponents.AuxiliaryDataAdapter
{
	public abstract class AuxiliaryDataAdapter : ComponentDataAdapterBase, IAuxiliaryDataAdapter
	{


		public IList<VectoRunData.AuxData> CreateAuxiliaryData(IAuxiliariesDeclarationInputData auxInputData,
			IBusAuxiliariesDeclarationData busAuxData,
			MissionType mission,
			VehicleClass hvdClass,
			Meter vehicleLength,
			int? numSteeredAxles,
			VectoSimulationJobType jobType, bool batteryOnlyHybridMode)
		{
			CheckDeclarationMode(auxInputData, "AuxiliariesData");
			return DoCreateAuxiliaryData(auxInputData, busAuxData, mission, hvdClass, vehicleLength, numSteeredAxles, jobType, batteryOnlyHybridMode);
		}

		public abstract AuxiliaryConfig CreateBusAuxiliariesData(Mission mission, IVehicleDeclarationInputData primaryVehicle, VectoRunData runData);

		protected abstract IList<VectoRunData.AuxData> DoCreateAuxiliaryData(
			IAuxiliariesDeclarationInputData auxInputData,
			IBusAuxiliariesDeclarationData busAuxData, MissionType mission, VehicleClass hdvClass, Meter vehicleLength,
			int? numSteeredAxles, VectoSimulationJobType jobType, bool batteryOnlyHybridMode);

		protected static bool CreateConditioningAux(VectoSimulationJobType jobType)
		{
			if (jobType == VectoSimulationJobType.ConventionalVehicle) {
				return false;
			} else {
				return true;
			}
		}
	}

	
}