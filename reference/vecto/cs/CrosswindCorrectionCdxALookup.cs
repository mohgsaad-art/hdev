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

using System.Collections.Generic;
using System.Linq;
using TUGraz.VectoCommon.Exceptions;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.InputData.Reader.ComponentData;

namespace TUGraz.VectoCore.Models.SimulationComponent.Data
{
	public class CrosswindCorrectionCdxALookup : LoggingObject, ICrossWindCorrection
	{
		protected readonly List<CrossWindCorrectionCurveReader.CrossWindCorrectionEntry> Entries;

        public CrosswindCorrectionCdxALookup(SquareMeter airDragArea, SquareMeter deltaAirDragAreaIMC, 
			List<CrossWindCorrectionCurveReader.CrossWindCorrectionEntry> entries,
			CrossWindCorrectionMode correctionMode)
		{
			AirDragArea = airDragArea;
			DeltaAirDragAreaIMC = deltaAirDragAreaIMC;
			CorrectionMode = correctionMode;
			Entries = entries;
		}

		public CrossWindCorrectionMode CorrectionMode { get; }

		public SquareMeter AirDragArea { get; }

		public SquareMeter DeltaAirDragAreaIMC { get; }

		public string[] SerializedEntries
		{
			get {
				return Entries.Select(x => $"{x.Velocity.AsKmph} [km/h] - {x.EffectiveCrossSectionArea}").ToArray();
			}
		}

		public AirDragLossResult AverageAirDragPowerLoss(DrivingCycleData.DrivingCycleEntry positionInCycle, MeterPerSecond v1, MeterPerSecond v2, KilogramPerCubicMeter airDensity)
		{
			var vAverage = (v1 + v2) / 2;
			var cdA_Base = EffectiveAirDragArea(vAverage);

			var cdA = cdA_Base + DeltaAirDragAreaIMC;
			// compute the average force within the current simulation interval
			// P(t) = k * CdA * v(t)^3  , v(t) = v0 + a * t  // P_avg = 1/T * Integral P(t) dt
			// => P_avg = (CdA * rho/2)/(4*a * dt) * (v2^4 - v1^4) // a = (v2-v1)/dt
			// -> P_avg = (CdA * rho/2) * (v2^4 - v1^4) / (v2 - v1) = (CdA * rho/2) * (v1 + v2) * (v1^2 + v2^2)
			var powerLoss = (airDensity / (2.0 * 4) * cdA * (v1 + v2) * (v1 * v1 + v2 * v2)).Cast<Watt>();
			return new AirDragLossResult(powerLoss, cdA, vAverage);
		}

		protected internal SquareMeter EffectiveAirDragArea(MeterPerSecond x)
		{
			var p = Entries.GetSection(c => c.Velocity < x);

			if (!x.IsBetween(p.Item1.Velocity, p.Item2.Velocity)) {
                throw new VectoException("CrossWindCorrection Extrapolation: v = {0} (max = {1})", x.ConvertToKiloMeterPerHour(),
                    p.Item2.Velocity.ConvertToKiloMeterPerHour());
			}

			return VectoMath.Interpolate(p.Item1.Velocity, p.Item2.Velocity,
				p.Item1.EffectiveCrossSectionArea, p.Item2.EffectiveCrossSectionArea, x);
		}

		
	}
}