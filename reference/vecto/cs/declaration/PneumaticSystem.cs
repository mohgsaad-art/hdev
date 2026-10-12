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
using System.Data;
using System.Linq;
using TUGraz.VectoCommon.InputData;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Utils;

namespace TUGraz.VectoCore.Models.Declaration.Auxiliaries
{
	public sealed class PneumaticSystem : LookupData<MissionType, string, AuxDemandEntry>, IDeclarationAuxiliaryTable, IDeclarationAuxiliaryArchitectureTable, IDeclarationAuxiliaryFullyElectricTable, IDeclarationAuxiliaryElectricPowerTable
	{
		private IDeclarationAuxiliaryArchitectureTable _declarationAuxiliaryArchitectureTableImplementation = new PneumaticSystemArchitectureTable();
		private IDeclarationAuxiliaryFullyElectricTable _declarationAuxiliaryFullyElectricTableImplementation = new PneumaticSystemFullyElectricTable();
		private IDeclarationAuxiliaryElectricPowerTable _declarationAuxiliaryElectricPowerTableImplementation = new PneumaticSystemElectricPowerTable();
		protected override string ResourceId => DeclarationData.DeclarationDataResourcePrefix + ".VAUX.PS-Table.csv";

		protected override string ErrorMessage => "Auxiliary Lookup Error: No value found for Pneumatic System. Mission: '{0}', Technology: '{1}'";

		protected override void ParseData(DataTable table)
		{
			foreach (DataRow row in table.Rows) {
				var technology = row.Field<string>("technology");
				foreach (DataColumn col in table.Columns.Cast<DataColumn>().Skip(table.Columns.IndexOf("fullyelectric") + 1)) {
					if (col.Caption == "longhaul_el")
					{
						break;
					}
					if (col.Caption != "technology") {
						Data[Tuple.Create(col.Caption.ParseEnum<MissionType>(), technology)] = new AuxDemandEntry() {
							PowerDemand = row.ParseDouble(col.Caption).SI<Watt>()
						};
					}

					
				}
			}
		}

		public string[] GetTechnologies()
		{
			return Data.Keys.Select(x => x.Item2).Distinct().ToArray();
		}

		#region Implementation of IDeclarationAuxiliaryArchitectureTable

		public bool IsApplicable(VectoSimulationJobType simType, string technology)
		{
			return _declarationAuxiliaryArchitectureTableImplementation.IsApplicable(simType, technology);
		}

		private class PneumaticSystemArchitectureTable : AbstractAuxiliaryVehicleArchitectureLookup
		{
			#region Overrides of LookupData

			protected override string ResourceId => DeclarationData.DeclarationDataResourcePrefix + ".VAUX.PS-Table.csv";

			#endregion
		}


		#endregion

		#region Implementation of IDeclarationAuxiliaryFullyElectricTable

		public bool IsFullyElectric(string technology)
		{
			return _declarationAuxiliaryFullyElectricTableImplementation.IsFullyElectric(technology);
		}

		public string[] FullyElectricTechnologies()
		{
			return _declarationAuxiliaryFullyElectricTableImplementation.FullyElectricTechnologies();
		}

		private class PneumaticSystemFullyElectricTable : AbstractAuxiliaryFullyElectricLookup
		{
			#region Overrides of LookupData

			protected override string ResourceId => DeclarationData.DeclarationDataResourcePrefix + ".VAUX.PS-Table.csv";

			#endregion
		}

		#endregion




		#region Implementation of IDeclarationAuxiliaryElectricPowerTable

		public Watt GetElectricPowerDemand(MissionType mission, string technology)
		{
			return _declarationAuxiliaryElectricPowerTableImplementation.GetElectricPowerDemand(mission, technology);
		}

		private class PneumaticSystemElectricPowerTable : LookupData<MissionType, string, AuxDemandEntry>, IDeclarationAuxiliaryElectricPowerTable
		{
			#region Overrides of LookupData

			protected override string ResourceId => DeclarationData.DeclarationDataResourcePrefix + ".VAUX.PS-Table.csv";
			protected override string ErrorMessage => "Auxiliary Lookup Error: No fully electric value found for Pneumatic System. Mission: '{0}', Technology: '{1}'";
			protected override void ParseData(DataTable table)
			{
				foreach (DataRow row in table.Rows)
				{
					
					var electric = row.ParseBoolean("fullyelectric");
					if (!electric)
					{
						continue;
					}
					var technology = row["technology"].ToString();
					foreach (DataColumn col in table.Columns.Cast<DataColumn>().Skip(table.Columns.IndexOf("longhaul_el")))
					{
						Data[Tuple.Create(col.Caption.Replace("_el", "").ParseEnum<MissionType>(), technology)] = new AuxDemandEntry()
						{
							PowerDemand = row.ParseDouble(col.Caption).SI<Watt>()
						};
					}
				}
			}

			#endregion

			#region Implementation of IDeclarationAuxiliaryElectricPowerTable

			public Watt GetElectricPowerDemand(MissionType mission, string technology)
			{
				return Lookup(mission, technology).PowerDemand;
			}

			#endregion
		}

		#endregion
	}
}