using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using TUGraz.VectoCommon.Exceptions;
using TUGraz.VectoCommon.InputData;
using TUGraz.VectoCore.Utils;

namespace TUGraz.VectoCore.Models.Declaration.Auxiliaries
{
	/// <summary>
	/// Maps the first columns of an auxiliary csv to a dictionary Dictionary<string technology, string arch>
	/// </summary>
	public abstract class AbstractAuxiliaryVehicleArchitectureLookup : LookupData<string, string, bool>, IDeclarationAuxiliaryArchitectureTable
	{
		public static Dictionary<VectoSimulationJobType, string> ArchitectureNameMapping =
			new Dictionary<VectoSimulationJobType, string>() {
				{VectoSimulationJobType.BatteryElectricVehicle, "pev"},
				{VectoSimulationJobType.SerialHybridVehicle, "s-hev"},
				{VectoSimulationJobType.ParallelHybridVehicle, "p-hev"},
				{VectoSimulationJobType.IHPC,"p-hev" },
				{VectoSimulationJobType.ConventionalVehicle, "conventional"},
				{VectoSimulationJobType.IEPC_S, "s-hev"},
				{VectoSimulationJobType.IEPC_E, "pev"},
				{VectoSimulationJobType.FCHV, "pev"},
				{VectoSimulationJobType.FCHV_IEPC, "pev"},
				{VectoSimulationJobType.Multiple_PEV, "pev"},
				{VectoSimulationJobType.Multiple_FCHV, "pev"},
				{VectoSimulationJobType.Multiple_SHEV, "s-hev" }
			};

		protected override string ErrorMessage =>
			"Auxiliary Lookup Error: No value found for Fan. Technology: '{0}', Architecture: '{1}'";
		#region Overrides of LookupData

		protected override void ParseData(DataTable table)
		{
			foreach (DataRow row in table.Rows) {
				var name = row["technology"].ToString();
				foreach (DataColumn col in table.Columns.Cast<DataColumn>().Skip(1).Take(4)) {
					Data[Tuple.Create(name, col.Caption)] = row.ParseBoolean(col.Caption);
				}
			}
		}

		#endregion

		#region Implementation of IDeclarationAuxiliaryTable

		public string[] GetTechnologies() => Data.Keys.Select(x => x.Item1).Distinct().ToArray();


		public bool IsApplicable(VectoSimulationJobType simType, string technology)
		{
			if (!GetTechnologies().Contains(technology)) {
				throw new VectoException($"Auxiliary Lookup Error: Unknown technology: '{technology}' valid technologies are '{string.Join(",", GetTechnologies())}'");
			}

			if (!ArchitectureNameMapping.ContainsKey(simType)) {
				throw new VectoException($"No Architecture mapping for {simType.ToString()}");
			}

			var arch = ArchitectureNameMapping[simType];
			return Lookup(technology, arch);
		}

		#endregion
	}
}