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

using System.Data;
using System.Diagnostics;
using System.Linq;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Utils;

namespace TUGraz.VectoCore.Models.Declaration
{
	public sealed class AirDrag : LookupData<string, AirDrag.Entry>
	{
		protected override string ResourceId => DeclarationData.DeclarationDataResourcePrefix + ".VCDV.VCDV_parameters.csv";

		protected override string ErrorMessage => "AirDrag Lookup Error: no value found. Key: '{0}'";

		protected override void ParseData(DataTable table)
		{
			Data = table.Rows.Cast<DataRow>().ToDictionary(
				row => row.Field<string>("Parameters"),
				row => new Entry(row.ParseDouble("a1").SI<SquareMeter>(),
					row.ParseDouble("a2").SI<SquareMeter>(),
					row.ParseDouble("a3").SI<SquareMeter>()));
		}

		[DebuggerDisplay("A1: {A1}, A2: {A2}, A3: {A3}")]
		public struct Entry
		{
			public readonly SquareMeter A1;
			public readonly SquareMeter A2;
			public readonly SquareMeter A3;

			public Entry(SquareMeter a1, SquareMeter a2, SquareMeter a3)
			{
				A1 = a1;
				A2 = a2;
				A3 = a3;
			}
		}
	}
}
