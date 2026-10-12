using System;
using System.Data;
using System.Linq;
using TUGraz.VectoCommon.InputData;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Utils;

namespace TUGraz.VectoCore.Models.Declaration.Auxiliaries
{
	public class Conditioning
	{
		private LorryConditioning _lorryConditioning = new LorryConditioning();
		private BusConditioning _busConditioning = new BusConditioning();

		private FCHVLorryConditioning _fchvLorryConditioning = new FCHVLorryConditioning();
		private FCHVBusConditioning _fchvBusConditioning = new FCHVBusConditioning();

		public Watt LookupPowerDemand(VehicleClass hdvClass, VectoSimulationJobType jobType, MissionType mission)
		{
			var FCHV_JOBS = new[] { VectoSimulationJobType.FCHV, VectoSimulationJobType.FCHV_IEPC, VectoSimulationJobType.Multiple_FCHV };
			if (FCHV_JOBS.Contains(jobType))
			{
				return hdvClass.IsBus()
				? _fchvBusConditioning.Lookup(mission).PowerDemand
				: _fchvLorryConditioning.Lookup(mission).PowerDemand;
			}

			return hdvClass.IsBus()
				? _busConditioning.Lookup(mission).PowerDemand
				: _lorryConditioning.Lookup(mission).PowerDemand;
		}

		private class LorryConditioning : LookupData<MissionType, AuxDemandEntry>
		{
			#region Overrides of LookupData

			protected override string ResourceId => DeclarationData.DeclarationDataResourcePrefix + ".VAUX.Cond-Table.csv";
			protected override void ParseData(DataTable table)
			{
				foreach (DataRow row in table.Rows) {
					foreach(DataColumn col in table.Columns.Cast<DataColumn>().Skip(1))
					{
						Data[col.Caption.ParseEnum<MissionType>()] = new AuxDemandEntry()
						{
							PowerDemand = row.ParseDouble(col.Caption).SI<Watt>()
						};
					}
				}
			}

			#endregion
		}

		private class BusConditioning : LorryConditioning
		{
			#region Overrides of LookupData
			protected override string ResourceId => DeclarationData.DeclarationDataResourcePrefix + ".VAUXBus.Cond-Table.csv";

			#endregion
		}


		private class FCHVLorryConditioning : LorryConditioning
		{
			#region Overrides of LookupData
			protected override string ResourceId => DeclarationData.DeclarationDataResourcePrefix + ".VAUX.FCHV-Cond-Table.csv";

			#endregion
		}

		private class FCHVBusConditioning : LorryConditioning
		{
			#region Overrides of LookupData
			protected override string ResourceId => DeclarationData.DeclarationDataResourcePrefix + ".VAUXBus.FCHV-Cond-Table.csv";

			#endregion
		}
	}
}