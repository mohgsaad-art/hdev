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

using System.Linq;
using TUGraz.VectoCommon.Exceptions;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Configuration;
using TUGraz.VectoCore.Models.Connector.Ports;
using TUGraz.VectoCore.Models.Connector.Ports.Impl;
using TUGraz.VectoCore.Models.Simulation;
using TUGraz.VectoCore.Models.Simulation.Data;
using TUGraz.VectoCore.Models.SimulationComponent.Data;
using TUGraz.VectoCore.OutputData;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
	public interface IPTOCycleController
	{
		void CommitSimulationStep(Second time, Second simulationInterval, IModalDataContainer container);
		Second GetNextCycleTime();
		Second Duration { get; }
		CycleData CycleData { get; }
	}

	public class PTOCycleController : PowertrainDrivingCycle, IIdleController
	{
		public ITnOutPort RequestPort
		{
			set => NextComponent = value;
		}

		public readonly Second Duration;

		protected Second IdleStart;

		public PTOCycleController(IVehicleContainer container, IDrivingCycleData cycle)
			: base(null, cycle)
		{
			DataBus = container;
			Duration = Data.Entries.Last().Time - Data.Entries.First().Time;
		}

		public IResponse Request(Second absTime, Second dt, NewtonMeter outTorque, PerSecond outAngularVelocity,
			bool dryRun = false)
		{
			if (outAngularVelocity != null) {
				throw new VectoException("{0} can only handle idle requests: AngularVelocity has to be null!",
					GetType().ToString());
			}
			if (!outTorque.IsEqual(0)) {
				throw new VectoException("{0} can only handle idle requests: Torque has to be 0!", GetType().ToString());
			}
			if (IdleStart == null) {
				IdleStart = absTime;
				PreviousState.InAngularVelocity = DataBus.EngineInfo.EngineSpeed;
			}
			return base.Request(absTime - IdleStart, dt);
			
		}

		public IResponse Initialize(NewtonMeter outTorque, PerSecond outAngularVelocity)
		{
			return new ResponseSuccess(this);
		}

		public void Reset()
		{
			CycleIterator.Reset();
			IdleStart = null;
		}

		public Second GetNextCycleTime()
		{
			if (CycleIterator.LastEntry && AbsTime.IsEqual(Duration)) {
				return null;
			}

			return CycleIterator.RightSample.Time - CycleIterator.LeftSample.Time;
		}

		protected override void DoWriteModalResults(Second time, Second simulationInterval, IModalDataContainer container)
		{

            base.DoWriteModalResults(time, simulationInterval, container);
            container[Constants.Auxiliaries.IDs.PTOConsumer] = CurrentState.InTorque *
                                                                (PreviousState.InAngularVelocity + CurrentState.InAngularVelocity) / 2;
            container[ModalResultField.P_ice_out] = 0.SI<Watt>();
        }


    }

	public class EPTOCycleController : IIdleControllerSwitcher, IUpdateable
	{
		internal readonly IDrivingCycleData Data;
		protected Second AbsTime { get; private set; }
		protected DrivingCycleEnumerator CycleIterator { get; }
		private bool _ptoActive;
		protected IVehicleContainer DataBus { get; set; }

		public Second Duration { get; private set; }


		public EPTOCycleController(IVehicleContainer container, IDrivingCycleData cycle)
		{
			DataBus = container;
			Data = cycle;
			Duration = Data.Entries.Last().Time - Data.Entries.First().Time;
		
			CycleIterator = new DrivingCycleEnumerator(Data);
			_ptoActive = false;
			AbsTime = 0.SI<Second>();
			
		}

		public CycleData CycleData
		{
			get => new CycleData() {
				LeftSample = _ptoActive ? CycleIterator.LeftSample : new DrivingCycleData.DrivingCycleEntry(),
			};
		} 


		public void CommitSimulationStep(Second time, Second simulationInterval, IModalDataContainer container)
		{
			if (_ptoActive) {
				CycleIterator.MoveNext();
				AbsTime += simulationInterval;
			}
		}

		public Second GetNextCycleTime()
		{
            if (CycleIterator.LastEntry && AbsTime.IsEqual(Duration))
            {
                return null;
            }

            return CycleIterator.RightSample.Time - CycleIterator.LeftSample.Time;
		}


		private void Reset()
		{
			CycleIterator.Reset();
			AbsTime = 0.SI<Second>();
		}

		#region Implementation of IIdleControllerSwitcher

		public void ActivatePTO()
		{
			_ptoActive = true;
		}

		public void ActivateIdle()
		{
			_ptoActive = false;
			Reset();
		}

		#endregion

		#region Implementation of IUpdateable

		public bool UpdateFrom(object other)
		{
			if (!DataBus.IsTestPowertrain)
			{
				throw new VectoException("Only components in a testpowertrain are allowed to be updated!");
			}
			if (other is EPTOCycleController otherPtoCycle) {
				Reset();
				while (this.CycleIterator.Current != otherPtoCycle.CycleIterator.Current) {
					this.CycleIterator.MoveNext();
				}

				this._ptoActive = otherPtoCycle._ptoActive;
				
				return true;
			} else {
				return false;
			}


		}

		#endregion
	}


}