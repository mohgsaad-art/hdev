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
using TUGraz.VectoCore.Utils;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
    /// <summary>
    ///     Class representing one Distance Based Driving Cycle
    /// </summary>
    public sealed class DistanceBasedDrivingCycle : StatefulProviderComponent
		<DistanceBasedDrivingCycle.DrivingCycleState, ISimulationOutPort, IDrivingCycleInPort, IDrivingCycleOutPort>,
		IDistanceBasedDrivingCycle, ISimulationOutPort, IDrivingCycleInPort, IDisposable, IUpdateable, IResetableVectoSimulationComponent
	{
		private const double LookaheadTimeSafetyMargin = 1.5;
		internal readonly IDrivingCycleData Data;
		internal DrivingCycleEnumerator CycleIntervalIterator;
		private bool _intervalProlonged;
		private Meter CycleEndDistance;

		
		private MeterPerSquareSecond StartAcceleration;
		private MeterPerSecond StartSpeed;

		private DrivingCycleData.DrivingCycleEntry Left => CycleIntervalIterator.LeftSample;

		private DrivingCycleData.DrivingCycleEntry Right => CycleIntervalIterator.RightSample;

		public IIdleControllerSwitcher IdleController { get; set; }

        public DistanceBasedDrivingCycle(IVehicleContainer container, IDrivingCycleData cycle) : 
			base(container, Constants.NOT_IN_AXLE_POWERTRAIN)
		{
			Data = cycle;
			CycleIntervalIterator = new DrivingCycleEnumerator(Data);
			CycleStartDistance = Data.Entries.Count > 0 ? Data.Entries.First().Distance : 0.SI<Meter>();
			CycleEndDistance = Data.Entries.Count > 0 ? Data.Entries.Last().Distance : 0.SI<Meter>();

			InitState(container);
		}

		#region Overrides of VectoSimulationComponent

		public void Reset(IVehicleContainer vehicleContainer)
		{
			CycleIntervalIterator.Reset();
			
			InitState(vehicleContainer);
			if (!(Initialize() is ResponseSuccess)) {
				throw new VectoException("Initialization failed");
			}

			;
		}

		#endregion

		private void InitState(IVehicleContainer container)
		{
			var first = Data.Entries.First();
			PreviousState = new DrivingCycleState {
				AbsTime = 0.SI<Second>(),
				WaitTime = 0.SI<Second>(),
				Distance = first.Distance,
				Altitude = first.Altitude,
				VehicleTargetSpeed = Data.Entries.First().VehicleTargetSpeed
			};
			CurrentState = PreviousState.Clone();

			StartSpeed = container.RunData.GearshiftParametersSinglePwt?.StartSpeed;
			StartAcceleration = container.RunData.GearshiftParametersSinglePwt?.StartAcceleration;

			if (container.RunData.AxlePowertrains.Count() > 0)
			{
				var gearParams = container.RunData.AxlePowertrains.First(x => x.GearshiftParameters != null).GearshiftParameters;
				
				StartSpeed = gearParams.StartSpeed;
				StartAcceleration = gearParams.StartAcceleration;
			}
		}

		public IResponse Initialize()
		{
			CycleStartDistance = Data.Entries.Count > 0 ? Data.Entries.First().Distance : 0.SI<Meter>();
			CycleEndDistance = Data.Entries.Count > 0 ? Data.Entries.Last().Distance : 0.SI<Meter>();
			var first = Data.Entries.First();
			PreviousState = new DrivingCycleState {
				AbsTime = 0.SI<Second>(),
				WaitTime = 0.SI<Second>(),
				Distance = first.Distance,
				Altitude = first.Altitude,
				VehicleTargetSpeed = Data.Entries.First().VehicleTargetSpeed
			};
			CurrentState = PreviousState.Clone();

			if (Left.VehicleTargetSpeed.IsEqual(0)) {
				var retVal = NextComponent.Initialize(StartSpeed,
					Left.RoadGradient, StartAcceleration);
				if (!(retVal is ResponseSuccess)) {
					throw new UnexpectedResponseException("DistanceBasedDrivingCycle.Initialize: Couldn't find start gear.", retVal);
				}
			}

			LastTargetspeedChange = SetLastTargetspeedChange(PreviousState.AbsTime, PreviousState, Left);

			return NextComponent.Initialize(Left.VehicleTargetSpeed,
				Left.RoadGradient);
		}

		public IResponse Request(Second absTime, Second dt)
		{
			throw new NotImplementedException("Distance Based Driving Cycle does not support time requests.");
		}

		public IResponse Request(Second absTime, Meter ds)
		{
			if (Left.Distance.IsEqual(PreviousState.Distance.Value())) {
				LastTargetspeedChange = SetLastTargetspeedChange(absTime, PreviousState, Left);
				var response = DoFirstSimulationInterval(absTime);
				if (response != null) {
					return response;
				}
			}
			if (CycleIntervalIterator.LastEntry && PreviousState.Distance.IsEqual(Right.Distance)) {
				CurrentState.Response = new ResponseCycleFinished(this);
				return CurrentState.Response;
			}

			var nextSpeedChange = GetSpeedChangeWithinSimulationInterval(ds);
			if (nextSpeedChange == null || ds.IsSmallerOrEqual(nextSpeedChange - PreviousState.Distance)) {
				if (nextSpeedChange == null || DataBus.VehicleInfo.VehicleSpeed.IsEqual(0.SI<MeterPerSecond>())) {
					CurrentState.Response = DriveDistance(absTime, ds);
					return CurrentState.Response;
				}
				var remainingDistance = nextSpeedChange - PreviousState.Distance - ds;
				var estimatedRemainingTime = remainingDistance / DataBus.VehicleInfo.VehicleSpeed;
				if (_intervalProlonged || remainingDistance.IsEqual(0.SI<Meter>()) ||
					estimatedRemainingTime.IsGreater(Constants.SimulationSettings.LowerBoundTimeInterval)) {
					CurrentState.Response = DriveDistance(absTime, ds);
					return CurrentState.Response;
				}
				Log.Debug("Extending distance by {0} to next sample point. ds: {1} new ds: {2}", remainingDistance, ds,
					nextSpeedChange - PreviousState.Distance);
				_intervalProlonged = true;
				CurrentState.Response = new ResponseDrivingCycleDistanceExceeded(this) {
					MaxDistance = nextSpeedChange - PreviousState.Distance
				};
				return CurrentState.Response;
			}

			if (DataBus.VehicleInfo.VehicleSpeed.IsGreater(0) && Right.Distance.IsSmaller(CycleEndDistance)) {
				var distanceToSpeedChange = nextSpeedChange - PreviousState.Distance;
				var estimatedTimeToSpeedChange = distanceToSpeedChange / DataBus.VehicleInfo.VehicleSpeed;
				if (estimatedTimeToSpeedChange.IsSmaller(Constants.SimulationSettings.LowerBoundTimeInterval / 2) &&
					DataBus.VehicleInfo.VehicleSpeed.IsSmaller(DataBus.DriverInfo.ApplyOverspeed(Left.VehicleTargetSpeed), 0.1.KMPHtoMeterPerSecond()) &&
					DataBus.VehicleInfo.VehicleSpeed.IsSmallerOrEqual( DataBus.DriverInfo.ApplyOverspeed(Right.VehicleTargetSpeed), 0.1.KMPHtoMeterPerSecond())) {
					CurrentState.Response = DriveDistance(absTime, ds);
					return CurrentState.Response;
				}
			}

			// only drive until next sample point in cycle with speed change
			Log.Debug("Limiting distance to next sample point {0}",
				Right.Distance - PreviousState.Distance);
			CurrentState.Response = new ResponseDrivingCycleDistanceExceeded(this) {
				MaxDistance = nextSpeedChange - PreviousState.Distance
			};
			return CurrentState.Response;
		}

		private SpeedChangeEntry SetLastTargetspeedChange(Second absTime, DrivingCycleState previousState, DrivingCycleData.DrivingCycleEntry left)
		{
			return new SpeedChangeEntry {
				PreviousTargetSpeed = previousState.VehicleTargetSpeed,
				AbsTime = absTime,
				Altitude = left.Altitude,
				NewTargetSpeed = left.VehicleTargetSpeed,
				Distance = left.Distance
			};
		}

		private IResponse DoFirstSimulationInterval(Second absTime)
		{
// we are exactly on an entry in the cycle.
			var stopTime = Left.PTOActive == PTOActivity.PTOActivityDuringStop && IdleController != null
				? Left.StoppingTime + IdleController.Duration
				: Left.StoppingTime;

			if (stopTime.IsGreater(0) && PreviousState.WaitTime.IsSmaller(stopTime)) {
				// stop for certain time unless we've already waited long enough ...

				// we are stopping: ensure that velocity is 0.
				if (!Left.VehicleTargetSpeed.IsEqual(0)) {
					Log.Warn("Stopping Time requested in cycle but target-velocity not zero. distance: {0}, target speed: {1}",
						Left.StoppingTime, Left.VehicleTargetSpeed);
					throw new VectoSimulationException("Stopping Time only allowed when target speed is zero!");
				}
				var dt = GetStopTimeInterval();
				if (dt == null) {
					CurrentState.WaitPhase++;
					dt = GetStopTimeInterval();
				}
				CurrentState.Response = DriveTimeInterval(absTime, dt);
				return CurrentState.Response;
			}
			return null;
		}

		private Second GetStopTimeInterval()
		{
			if (Left.PTOActive != PTOActivity.PTOActivityDuringStop || IdleController == null) {
				if ((Left.StoppingTime - PreviousState.WaitTime).IsGreater(2 * Constants.SimulationSettings.TargetTimeInterval,
					0.1 * Constants.SimulationSettings.TargetTimeInterval)) {
					return 2 * Constants.SimulationSettings.TargetTimeInterval;
				}
				return Left.StoppingTime - PreviousState.WaitTime;
			}
			if (Left.StoppingTime.IsGreater(6 * Constants.SimulationSettings.TargetTimeInterval)) {
				// 7 phases
				return GetStopTimeIntervalSevenPhasesPTO();
			}
			if (Left.StoppingTime.IsGreater(0)) {
				// 3 phases
				return GetStopTimeIntervalThreePhasesPTO();
			}
			// we have a pto cycle without stopping time.
			IdleController.ActivatePTO();
			return IdleController.GetNextCycleTime();
		}

		private Second GetStopTimeIntervalThreePhasesPTO()
		{
			switch (CurrentState.WaitPhase) {
				case 1:
				case 3:
					CurrentState.WaitPhase++;
					IdleController.ActivateIdle();
					PTOActive = false;
					return Left.StoppingTime / 2;
				case 2:
					PTOActive = true;
					IdleController.ActivatePTO();
					return IdleController.GetNextCycleTime();
			}
			return null;
		}

		private Second GetStopTimeIntervalSevenPhasesPTO()
		{
			switch (CurrentState.WaitPhase) {
				case 1:
				case 5:
					CurrentState.WaitPhase++;
					IdleController.ActivateIdle();
					PTOActive = false;
					return Constants.SimulationSettings.TargetTimeInterval;
				case 3:
				case 7:
					CurrentState.WaitPhase++;
					return Constants.SimulationSettings.TargetTimeInterval;
				case 2:
				case 6:
					CurrentState.WaitPhase++;
					return Left.StoppingTime / 2 - 2 * Constants.SimulationSettings.TargetTimeInterval;
				case 4:
					PTOActive = true;
					IdleController.ActivatePTO();
					return IdleController.GetNextCycleTime();
			}
			return null;
		}

		private IResponse DriveTimeInterval(Second absTime, Second dt)
		{
			CurrentState.AbsTime = absTime;
			CurrentState.WaitTime = PreviousState.WaitTime + dt;
			CurrentState.Gradient = ComputeGradient(0.SI<Meter>());
			CurrentState.VehicleTargetSpeed = Left.VehicleTargetSpeed;
			CurrentState.SimulationDistance = 0.SI<Meter>();

			return NextComponent.Request(absTime, dt, Left.VehicleTargetSpeed, CurrentState.Gradient);
		}

		private IResponse DriveDistance(Second absTime, Meter ds)
		{
			var nextSpeedChanges = LookAhead(Constants.SimulationSettings.BrakeNextTargetDistance);
			if (nextSpeedChanges.Count > 0 && !CurrentState.RequestToNextSamplePointDone) {
				CurrentState.RequestToNextSamplePointDone = true;
				Log.Debug("current distance is close to the next speed change: {0}",
					nextSpeedChanges.First().Distance - PreviousState.Distance);
				return new ResponseDrivingCycleDistanceExceeded(this) {
					MaxDistance = Constants.SimulationSettings.BrakeNextTargetDistance
				};
			}

			CurrentState.WaitPhase = 0;
			//CurrentState.Distance = PreviousState.Distance + ds;
			CurrentState.SimulationDistance = ds;
			CurrentState.VehicleTargetSpeed = Left.VehicleTargetSpeed;
			CurrentState.Gradient = ComputeGradient(ds);
			CurrentState.Highway = Left.Highway; // && Right.Highway;

			var retVal = NextComponent.Request(absTime, ds, CurrentState.VehicleTargetSpeed, CurrentState.Gradient);
			if (retVal is ResponseFailTimeInterval r) { 
				var debugRetVal = NextComponent.Request(absTime, r.DeltaT, 0.SI<MeterPerSecond>(), CurrentState.Gradient);
				retVal = NextComponent.Request(absTime, ds, CurrentState.VehicleTargetSpeed, CurrentState.Gradient);
			}
			CurrentState.AbsTime = absTime;
			if (retVal is ResponseSuccess) {
				CurrentState.Distance = PreviousState.Distance + retVal.SimulationDistance;
			}
			return retVal;
		}

		protected override void DoWriteModalResults(Second time, Second simulationInterval, IModalDataContainer container)
		{
			if (CurrentState == null) {
				return;
			}
			container[ModalResultField.dist] = CurrentState.Distance; // (CurrentState.Distance + PreviousState.Distance) / 2.0;
			container[ModalResultField.simulationDistance] = CurrentState.SimulationDistance;
			container[ModalResultField.v_targ] = CurrentState.VehicleTargetSpeed;
			container[ModalResultField.grad] = CurrentState.Gradient != null
				? (Math.Tan(CurrentState.Gradient.Value()) * 100).SI<Scalar>()
				: null;
			container[ModalResultField.altitude] = CurrentState.Altitude;
			container[ModalResultField.Highway] = CurrentState.Highway ? 1 : 0;

			if (IdleController != null) {
				IdleController.CommitSimulationStep(time, simulationInterval, container);
			}
		}

		protected override void DoCommitSimulationStep(Second time, Second simulationInterval)
		{
			if (CurrentState.Response != null && !(CurrentState.Response is ResponseSuccess)) {
				throw new VectoSimulationException("Previous request did not succeed!");
			}

			PreviousState = CurrentState;
			CurrentState = CurrentState.Clone();
			_intervalProlonged = false;


			var stopTime = Left.PTOActive == PTOActivity.PTOActivityDuringStop && IdleController != null
				? Left.StoppingTime + IdleController.Duration
				: Left.StoppingTime;

			// separately test for equality and greater than to have tolerance for equality comparison
			if (stopTime.IsEqual(0)) {
				while (stopTime.IsEqual(0) && CurrentState.Distance.IsGreaterOrEqual(Right.Distance) &&
						!CycleIntervalIterator.LastEntry) {
					// we have reached the end of the current interval in the cycle, move on...
					CycleIntervalIterator.MoveNext();

					stopTime = Left.PTOActive == PTOActivity.PTOActivityDuringStop && IdleController != null
						? Left.StoppingTime + IdleController.Duration
						: Left.StoppingTime;
				}
			} else {
				if (stopTime.IsEqual(PreviousState.WaitTime)) {
					// we needed to stop at the current interval in the cycle and have already waited enough time, move on..
					if (IdleController != null) {
						IdleController.ActivateIdle();
					}
					CycleIntervalIterator.MoveNext();
				}
			}
		}

		private Radian ComputeGradient(Meter ds)
		{
			var cycleIterator = CycleIntervalIterator.Clone();
			while (cycleIterator.RightSample.Distance < PreviousState.Distance + ds && !cycleIterator.LastEntry) {
				cycleIterator.MoveNext();
			}
			var leftSamplePoint = cycleIterator.LeftSample;
			var rightSamplePoint = cycleIterator.RightSample;

			if (leftSamplePoint.Distance.IsEqual(rightSamplePoint.Distance)) {
				return leftSamplePoint.RoadGradient;
			}
			if (ds.IsEqual(0.SI<Meter>())) {
				return leftSamplePoint.RoadGradient;
			}
			CurrentState.Altitude = VectoMath.Interpolate(leftSamplePoint.Distance, rightSamplePoint.Distance,
				leftSamplePoint.Altitude, rightSamplePoint.Altitude, PreviousState.Distance + ds);

			var gradient = VectoMath.InclinationToAngle(((CurrentState.Altitude - PreviousState.Altitude) /
														ds).Value());
			//return 0.SI<Radian>();
			return gradient;
		}

		private Meter GetSpeedChangeWithinSimulationInterval(Meter ds)
		{
			var leftSamplePoint = Left;
			var cycleIterator = CycleIntervalIterator.Clone();

			do {
				if (!leftSamplePoint.VehicleTargetSpeed.IsEqual(cycleIterator.RightSample.VehicleTargetSpeed)) {
					return cycleIterator.RightSample.Distance;
				}
			} while (cycleIterator.RightSample.Distance < PreviousState.Distance + ds && cycleIterator.MoveNext());
			if (cycleIterator.LastEntry) {
				return cycleIterator.RightSample.Distance;
			}
			return null;
		}

		/// <summary>
		/// Progress of the distance in the driving cycle.
		/// </summary>
		public double Progress =>
			Data.Entries.Count > 0
				? (CurrentState.Distance.Value() - Data.Entries.First().Distance.Value()) /
				(Data.Entries.Last().Distance.Value() - Data.Entries.First().Distance.Value())
				: 0;

		public Second StopTime => CycleIntervalIterator.LeftSample.StoppingTime;

		public Meter CycleStartDistance { get; internal set; }

		public IReadOnlyList<DrivingCycleData.DrivingCycleEntry> LookAhead(Meter lookaheadDistance)
		{
			var retVal = new List<DrivingCycleData.DrivingCycleEntry>();

			var cycleIterator = CycleIntervalIterator.Clone();
			var velocity = cycleIterator.LeftSample.VehicleTargetSpeed;

			do {
				if (cycleIterator.RightSample.VehicleTargetSpeed.IsEqual(velocity)) {
					continue;
				}
				var lookaheadEntry = retVal.Find(x => x.Distance == cycleIterator.RightSample.Distance);
				if (lookaheadEntry != null) {
					// an entry may occur twice when vehicle stops (one entry with v=0 and the other with drive on after stop)
					// only use the one with min. speed
					if (cycleIterator.RightSample.VehicleTargetSpeed < lookaheadEntry.VehicleTargetSpeed) {
						retVal.Remove(lookaheadEntry);
						retVal.Add(cycleIterator.RightSample);
					}
				} else {
					retVal.Add(cycleIterator.RightSample);
				}
				velocity = cycleIterator.RightSample.VehicleTargetSpeed;
				if (velocity.IsEqual(0.KMPHtoMeterPerSecond())) {
					// do not look beyond vehicle stop
					break;
				}
			} while (cycleIterator.MoveNext() && cycleIterator.RightSample.Distance < PreviousState.Distance + lookaheadDistance);
			if (retVal.Count > 0) {
				retVal = retVal.Where(x => x.Distance <= PreviousState.Distance + lookaheadDistance).ToList();
				retVal.Sort((x, y) => x.Distance.CompareTo(y.Distance));
			}
			return retVal;
		}

		public IReadOnlyList<DrivingCycleData.DrivingCycleEntry> LookAhead(Second time)
		{
			return LookAhead(LookaheadTimeSafetyMargin * DataBus.VehicleInfo.VehicleSpeed * time);
		}

		public SpeedChangeEntry LastTargetspeedChange { get; private set; }

		public void FinishSimulation()
		{
			Data.Finish();
		}

		public CycleData CycleData {
			get
			{
				return new CycleData
				{
					AbsTime = CurrentState.AbsTime,
					AbsDistance = CurrentState.Distance,
					LeftSample = Left,
					RightSample = CycleIntervalIterator.RightSample,
				};
			}
		}
			
			

		public bool PTOActive { get; private set; }

		public DrivingCycleData.DrivingCycleEntry CycleLookAhead(Meter distance)
		{
			var absDistance = CurrentState.Distance + distance;
			var myIterator = CycleIntervalIterator.Clone();

			if (absDistance > Data.Entries.Last().Distance) {
				return ExtrapolateCycleEntry(absDistance, Data.Entries.Last());
			}
			while (myIterator.RightSample.Distance < absDistance) {
				myIterator.MoveNext();
			}

			return InterpolateCycleEntry(absDistance, myIterator);
		}

		private DrivingCycleData.DrivingCycleEntry InterpolateCycleEntry(Meter absDistance,
			DrivingCycleEnumerator lookahead)
		{
			var retVal = new DrivingCycleData.DrivingCycleEntry(lookahead.RightSample) {
				Distance = absDistance,
				Altitude = VectoMath.Interpolate(lookahead.LeftSample.Distance, lookahead.RightSample.Distance, lookahead.LeftSample.Altitude,
					lookahead.RightSample.Altitude, absDistance)
			};

			//retVal.RoadGradient =
			//	((retVal.Altitude - CurrentState.Altitude) / (absDistance - CurrentState.Distance)).Value().SI<Radian>();

			return retVal;
		}

		private DrivingCycleData.DrivingCycleEntry ExtrapolateCycleEntry(Meter absDistance,
			DrivingCycleData.DrivingCycleEntry lookahead)
		{
			var retVal = new DrivingCycleData.DrivingCycleEntry(lookahead) {
				Distance = absDistance,
				Altitude = lookahead.Altitude + lookahead.RoadGradient * (absDistance - lookahead.Distance),
			};

			retVal.RoadGradient =
				((retVal.Altitude - CurrentState.Altitude) / (absDistance - CurrentState.Distance)).Value().SI<Radian>();

			return retVal;
		}

		public Meter Altitude => PreviousState.Altitude;

		public Radian RoadGradient => CurrentState.Gradient;

		public MeterPerSecond TargetSpeed => CurrentState.VehicleTargetSpeed;


		public sealed class DrivingCycleState
		{
			public DrivingCycleState Clone()
			{
				return new DrivingCycleState {
					AbsTime = AbsTime,
					Distance = Distance,
					VehicleTargetSpeed = VehicleTargetSpeed,
					Altitude = Altitude,
					WaitPhase = WaitPhase,
					// WaitTime is not cloned on purpose!
					WaitTime = 0.SI<Second>(),
					Response = null
				};
			}

			public Second AbsTime;

			public Meter Distance;

			public Second WaitTime;

			public uint WaitPhase;

			public MeterPerSecond VehicleTargetSpeed;

			public Meter Altitude;

			public Radian Gradient;

			public IResponse Response;

			public bool RequestToNextSamplePointDone;

			public Meter SimulationDistance;

			public bool Highway;
		}

		public void Dispose()
		{
			CycleIntervalIterator.Dispose();
		}

		#region Implementation of IUpdateable

		protected override bool DoUpdateFrom(object other) {
			if (other is DistanceBasedDrivingCycle c) {
				PreviousState = c.PreviousState.Clone();
				CycleIntervalIterator = c.CycleIntervalIterator;
				//TODO MK-20220523 also allow updating from measuredspeeddrivingcycle?
				return true;
			}

			return false;
		}

		#endregion
	}
}
