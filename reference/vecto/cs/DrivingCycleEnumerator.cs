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
using TUGraz.VectoCore.Models.SimulationComponent.Data;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
	public sealed class DrivingCycleEnumerator : IEnumerator<DrivingCycleData.DrivingCycleEntry>
	{
		private int _currentCycleIndex;
		private readonly IDrivingCycleData _data;

		public DrivingCycleEnumerator(IDrivingCycleData data)
		{
			_currentCycleIndex = 0;
			_data = data;
			LastEntry = false;
		}

		public DrivingCycleEnumerator Previous()
		{
			var retVal = new DrivingCycleEnumerator(_data);
			retVal._currentCycleIndex = Math.Max(0, _currentCycleIndex - 1);
			return retVal;
		}

		public DrivingCycleEnumerator Clone()
		{
			return new DrivingCycleEnumerator(_data) {
				_currentCycleIndex = _currentCycleIndex,
				LastEntry = LastEntry
			};
		}

		public DrivingCycleData.DrivingCycleEntry Current => LeftSample;

		public DrivingCycleData.DrivingCycleEntry LeftSample => _data.Entries[_currentCycleIndex];

		public DrivingCycleData.DrivingCycleEntry RightSample => _currentCycleIndex + 1 >= _data.Entries.Count ? null : _data.Entries[_currentCycleIndex + 1];

		public bool LastEntry { get; private set; }

		object System.Collections.IEnumerator.Current => LeftSample;

		public bool MoveNext()
		{
			// cycleIndex has to be max. next to last (so that rightSample is still valid.
			if (_currentCycleIndex >= _data.Entries.Count - 2) {
				LastEntry = true;
				return false;
			}
			_currentCycleIndex++;
			if (_currentCycleIndex == _data.Entries.Count - 2) {
				LastEntry = true;
			}

			return true;
		}

		public void Reset()
		{
			_currentCycleIndex = 0;
			LastEntry = false;
		}

		public void Dispose() {}
	}
}