using System;
using System.Collections.Generic;
using System.Linq;
using TUGraz.VectoCommon.Exceptions;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Models.Connector.Ports;
using TUGraz.VectoCore.Models.Connector.Ports.Impl;
using TUGraz.VectoCore.Models.Simulation;
using TUGraz.VectoCore.Models.SimulationComponent.Data;
using TUGraz.VectoCore.OutputData;
using TUGraz.VectoCore.Configuration;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
    /// <summary>
    /// Represents a cycle which is directly connected to the electric system
    /// </summary>
    public class ElectricSystemDrivingCycle : StatefulProviderComponent<SimpleComponentState, ISimulationOutPort, ITnInPort, IElectricSystem>, 
		ITnInProvider,
		ISimulationOutPort, IDrivingCycleInfo
	{
		internal readonly IDrivingCycleData Data;
		protected internal readonly DrivingCycleEnumerator CycleIterator;

		protected Second AbsTime { get; set; }

		public ElectricSystemDrivingCycle(IVehicleContainer container, IDrivingCycleData cycle) : 
			base(container, Constants.NOT_IN_AXLE_POWERTRAIN)
		{
			Data = cycle;
			CycleIterator = new DrivingCycleEnumerator(Data);

			AbsTime = -1.SI<Second>();
		}

		#region Overrides of VectoSimulationComponent

		protected override void DoWriteModalResults(Second time, Second simulationInterval, IModalDataContainer container)
		{
			
		}

		#region Overrides of StatefulProviderComponent<SimpleComponentState,ISimulationOutPort,ITnInPort,IElectricSystem>

		protected override void DoCommitSimulationStep(Second time, Second simulationInterval)
		{
			CycleIterator.MoveNext();
			AdvanceState();
		}

		#endregion

		#endregion

		#region Implementation of ISimulationOutPort

		public IResponse Request(Second absTime, Meter ds)
		{
			throw new VectoSimulationException("Electric System Simulation can not handle distance request.");
		}

		public IResponse Request(Second absTime, Second dt)
		{
			// cycle finished (no more entries in cycle)
			if (CycleIterator.LastEntry && CycleIterator.RightSample.Time == absTime)
			{
				return new ResponseCycleFinished(this);
			}

			// interval exceeded
			if (CycleIterator.RightSample != null && (absTime + dt).IsGreater(CycleIterator.RightSample.Time))
			{
				return new ResponseFailTimeInterval(this)
				{
					AbsTime = absTime,
					DeltaT = CycleIterator.RightSample.Time - absTime
				};
			}

			//return DoHandleRequest(absTime, dt, CycleIterator.LeftSample.AngularVelocity);
			return null;
		}

		public IResponse Initialize()
		{
			throw new System.NotImplementedException();
		}

		public double Progress => Math.Max(0, AbsTime.Value() / Data.Entries.Last().Time.Value());

		#endregion

		public CycleData CycleData =>
			new CycleData
			{
				AbsTime = CycleIterator.LeftSample.Time,
				AbsDistance = null,
				LeftSample = CycleIterator.LeftSample,
				RightSample = CycleIterator.RightSample,
			};

		public bool PTOActive => true;
		public DrivingCycleData.DrivingCycleEntry CycleLookAhead(Meter distance)
		{
			throw new System.NotImplementedException();
		}

		public Meter Altitude => 0.SI<Meter>();
		public Radian RoadGradient => 0.SI<Radian>();
		public MeterPerSecond TargetSpeed => throw new NotImplementedException("Targetspeed in Powertrain not available?");
		public Second StopTime => CycleIterator.LeftSample.StoppingTime;
		public Meter CycleStartDistance => 0.SI<Meter>();
		public IReadOnlyList<DrivingCycleData.DrivingCycleEntry> LookAhead(Meter lookaheadDistance)
		{
			throw new System.NotImplementedException();
		}

		public IReadOnlyList<DrivingCycleData.DrivingCycleEntry> LookAhead(Second time)
		{
			var retVal = new List<DrivingCycleData.DrivingCycleEntry>();

			var iterator = CycleIterator.Clone();
			do
			{
				retVal.Add(iterator.RightSample);
			} while (iterator.MoveNext() && iterator.RightSample.Time < AbsTime + time);

			return retVal;
		}

		public SpeedChangeEntry LastTargetspeedChange => null;

		public void FinishSimulation()
		{
			Data.Finish();
		}

		protected override bool DoUpdateFrom(object other) => false;
	}
}