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
using System.Collections.Generic;
using System.Data;
using System.Linq;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Models.Declaration.Auxiliaries;
using TUGraz.VectoCore.Utils;

namespace TUGraz.VectoCore.Models.Declaration
{
	public sealed class HeatingVentilationAirConditioning : LookupData<MissionType, string, VehicleClass, AuxDemandEntry>,
		IDeclarationAuxiliaryTable
	{
		private List<string> Technologies;

	protected override string ResourceId => DeclarationData.DeclarationDataResourcePrefix + ".VAUX.HVAC-Table.csv";

		protected override string ErrorMessage => "Auxiliary Lookup Error: No value found for HVAC. Mission: '{0}', Technology: '{1}' , HDVClass: '{2}'";

		protected override void ParseData(DataTable table)
		{
			foreach (DataRow row in table.Rows) {
				var hdvClass = VehicleClassHelper.Parse(row.Field<string>("hdvgroup"));
				var technology = row.Field<string>("technology");
				foreach (DataColumn col in table.Columns) {
					var value = row.ParseDoubleOrGetDefault(col.Caption, double.NaN);
					if (col.Caption != "hdvgroup" && col.Caption != "technology" && !double.IsNaN(value)) {
						Data[Tuple.Create(col.Caption.ParseEnum<MissionType>(), technology, hdvClass)] = new AuxDemandEntry() {
							PowerDemand = value.SI<Watt>()
						};
					}
				}
			}
			Technologies = Data.Select(x => x.Key.Item2).Distinct().ToList();
		}

		public string[] GetTechnologies()
		{
			return Technologies.ToArray();
		}
	}
}