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
using System.Linq;
using TUGraz.VectoCommon.Exceptions;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Configuration;
using TUGraz.VectoCore.Models.Connector.Ports;
using TUGraz.VectoCore.Models.Connector.Ports.Impl;
using TUGraz.VectoCore.Models.Simulation;
using TUGraz.VectoCore.Models.Simulation.Data;
using TUGraz.VectoCore.Models.Simulation.DataBus;
using TUGraz.VectoCore.Models.Simulation.Impl;
using TUGraz.VectoCore.OutputData;
using TUGraz.VectoCore.Utils;
using DriverData = TUGraz.VectoCore.Models.SimulationComponent.Data.DriverData;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
    public enum DrivingAction
	{
		Halt = 0,
		Roll = 2,
		Coast = 4,
		Accelerate = 6,
		Brake = -5,
	}

	public class Driver :
		StatefulProviderComponent<Driver.DriverState, IDrivingCycleOutPort, IDriverDemandInPort, IDriverDemandOutPort>,
		IDriver, IDrivingCycleOutPort, IDriverDemandInPort, IDriverActions, IDriverInfo, IResetableVectoSimulationComponent
	{
		public DriverData DriverData { get; protected set; }

		protected readonly IDriverStrategy DriverStrategy;
		protected readonly bool smartBusAux;
		private bool? _previousGearboxDisengaged = null;

		public DrivingAction DrivingAction { get; protected internal set; }

		public Driver(IVehicleContainer container, DriverData driverData, IDriverStrategy strategy) : 
			base(container, Constants.NOT_IN_AXLE_POWERTRAIN)
		{
			DriverData = driverData;
			DriverStrategy = strategy;
			strategy.Driver = this;
			DriverAcceleration = 0.SI<MeterPerSquareSecond>();
			var busAux = container.RunData.BusAuxiliaries;
			smartBusAux = busAux != null && (busAux.PneumaticUserInputsConfig.SmartAirCompression ||
											busAux.ElectricalUserInputsConfig.AlternatorType == AlternatorType.Smart);
		}


		public IResponse Initialize(MeterPerSecond vehicleSpeed, Radian roadGradient)
		{
			DriverBehavior = vehicleSpeed.IsEqual(0) ? DrivingBehavior.Halted : DrivingBehavior.Driving;
			return NextComponent.Initialize(vehicleSpeed, roadGradient);
		}

		public IResponse Initialize(MeterPerSecond vehicleSpeed, Radian roadGradient,
			MeterPerSquareSecond startAcceleration)
		{
			DriverBehavior = vehicleSpeed.IsEqual(0) ? DrivingBehavior.Halted : DrivingBehavior.Driving;
			var retVal = NextComponent.Initialize(vehicleSpeed, roadGradient, startAcceleration);

			return retVal;
		}

		#region Implementation of IResetableVectoSimulationComponent

		public void Reset(IVehicleContainer vehicleContainer)
		{
			CurrentState = new DriverState();
			PreviousState = new DriverState();
			DriverAcceleration = 0.SI<MeterPerSquareSecond>();
		}

		#endregion

		public IResponse Request(Second absTime, Meter ds, MeterPerSecond targetVelocity, Radian gradient)
		{
			IterationStatistics.Increment(this, "Requests");

			Log.Debug("==== DRIVER Request (distance) ====");
			Log.Debug(
				"Request: absTime: {0},  ds: {1}, targetVelocity: {2}, gradient: {3} | distance: {4}, velocity: {5}, vehicle stopped: {6}",
				absTime, ds, targetVelocity, gradient, DataBus.MileageCounter.Distance, DataBus.VehicleInfo.VehicleSpeed, DataBus.VehicleInfo.VehicleStopped);

			var retVal = DriverStrategy.Request(absTime, ds, targetVelocity, gradient);

			CurrentState.Response = retVal;
			retVal.SimulationInterval = CurrentState.dt;
			retVal.Driver.Acceleration = CurrentState.Acceleration;

			return retVal;
		}

		public IResponse Request(Second absTime, Second dt, MeterPerSecond targetVelocity, Radian gradient)
		{
			IterationStatistics.Increment(this, "Requests");

			Log.Debug("==== DRIVER Request (time) ====");
			Log.Debug(
				"Request: absTime: {0},  dt: {1}, targetVelocity: {2}, gradient: {3} | distance: {4}, velocity: {5}, {6}: vehicle stopped: {7}",
				absTime, dt, targetVelocity, gradient, DataBus.MileageCounter.Distance, DataBus.VehicleInfo.VehicleSpeed,
				DataBus.GearboxesInfo.Select(x => $"Gear{x.AxleNumber.FormatAxleNumber()}: {x.Gear}").Join(), DataBus.VehicleInfo.VehicleStopped);

			var retVal = DriverStrategy.Request(absTime, dt, targetVelocity, gradient);

			CurrentState.Response = retVal;
			retVal.SimulationInterval = CurrentState.dt;
			retVal.Driver.Acceleration = CurrentState.Acceleration;

			return retVal;
		}

		public new IDataBus DataBus => base.DataBus;

		/// <summary>
		/// see documentation of IDriverActions
		/// </summary>
		/// <param name="absTime"></param>
		/// <param name="ds"></param>
		/// <param name="targetVelocity"></param>
		/// <param name="gradient"></param>
		/// <param name="previousResponse"></param>
		/// <returns></returns>
		/// <returns></returns>
		public IResponse DrivingActionAccelerate(Second absTime, Meter ds, MeterPerSecond targetVelocity,
			Radian gradient, IResponse previousResponse = null)
		{
			DrivingAction = DrivingAction.Accelerate;
			IterationStatistics.Increment(this, "Accelerate");
			Log.Debug("DrivingAction Accelerate");
			var operatingPoint = ComputeAcceleration(ds, targetVelocity);

			IResponse retVal = null;
			DriverAcceleration = operatingPoint.Acceleration;
			var response = previousResponse ?? NextComponent.Request(absTime, operatingPoint.SimulationInterval, operatingPoint.Acceleration, gradient, false);
			response.Driver.Acceleration = operatingPoint.Acceleration;

			switch (response) {
				case ResponseSuccess r:
					retVal = r; // => return
					break;
				case ResponseOverload _:
					break; // do nothing, searchOperatingPoint is called later on
				case ResponseEngineSpeedTooHigh _:
					break; // do nothing, searchOperatingPoint is called later on
				case ResponseUnderload r:
					// Delta is negative we are already below the Drag-load curve. activate brakes
					retVal = r; // => return, strategy should brake
					break;
				case ResponseFailTimeInterval r:
					// occurs only with AT gearboxes - extend time interval after gearshift!
					retVal = new ResponseDrivingCycleDistanceExceeded(this) {
						MaxDistance = r.Driver.Acceleration / 2 * r.DeltaT * r.DeltaT + DataBus.VehicleInfo.VehicleSpeed * r.DeltaT
					};
					break;
				case ResponseGearShift r:
					retVal = r;
					break;
				case ResponseBatteryEmpty _:
					return response;
				default:
					throw new UnexpectedResponseException("DrivingAction Accelerate.", response);
			}
			if (retVal == null) {
				// unhandled response (overload, delta > 0) - we need to search for a valid operating point..	

				OperatingPoint nextOperatingPoint;
				try {
					nextOperatingPoint = SearchOperatingPoint(absTime, ds, gradient, operatingPoint.Acceleration,
						response);
				} catch (VectoEngineSpeedTooLowException) {
					// in case of an exception during search the engine-speed got too low - gear disengaged, try roll action.
					nextOperatingPoint = SearchOperatingPoint(absTime, ds, gradient, operatingPoint.Acceleration,
						response);
				}

				if (nextOperatingPoint == null && absTime > 0 && DataBus.VehicleInfo.VehicleStopped) {
					Log.Info("No operating point found! Vehicle stopped! trying HALT action");
					DataBus.Brakes.BrakePower = 1.SI<Watt>();
					retVal = DrivingActionHalt(absTime, operatingPoint.SimulationInterval, 0.SI<MeterPerSecond>(), gradient);

					retVal.SimulationDistance = 0.SI<Meter>();
					retVal.Driver.Acceleration = 0.SI<MeterPerSquareSecond>();
					retVal.SimulationInterval = operatingPoint.SimulationInterval;
					retVal.Driver.OperatingPoint = new OperatingPoint() {
						Acceleration = retVal.Driver.Acceleration,
						SimulationDistance = retVal.SimulationDistance,
						SimulationInterval = operatingPoint.SimulationInterval
					};
					return retVal;
				}

				var limitedOperatingPoint = nextOperatingPoint;
				if (!DataBus.ClutchInfo().ClutchClosed(absTime)) {
					limitedOperatingPoint = LimitAccelerationByDriverModel(nextOperatingPoint,
						LimitationMode.LimitDecelerationDriver);
					Log.Debug("Found operating point for Drive/Accelerate. dt: {0}, acceleration: {1}",
						limitedOperatingPoint.SimulationInterval, limitedOperatingPoint.Acceleration);
				}
				if (limitedOperatingPoint == null) {
					throw new VectoException("DrivingActionAccelerate: Failed to find operating point");
				}
				DriverAcceleration = limitedOperatingPoint.Acceleration;
				retVal = NextComponent.Request(absTime, limitedOperatingPoint.SimulationInterval,
					limitedOperatingPoint.Acceleration,
					gradient, false);
				if (retVal != null) {
					retVal.Driver.Acceleration = limitedOperatingPoint.Acceleration;
				}

				switch (retVal) {
					case ResponseUnderload _:
						operatingPoint = limitedOperatingPoint;
						break; // acceleration is limited by driver model, operating point moves below drag curve
					case ResponseOverload _:
						// deceleration is limited by driver model, operating point moves above full load (e.g., steep uphill)
						// the vehicle/driver can't achieve an acceleration higher than deceleration curve, try again with higher deceleration
						if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission()) {
							Log.Info("AT Gearbox - Operating point resulted in an overload, searching again...");
							// search again for operating point, transmission may have shifted inbetween
							nextOperatingPoint = SearchOperatingPoint(absTime, ds, gradient, operatingPoint.Acceleration,
								response);
							if (nextOperatingPoint == null) {
								throw new VectoException("DrivingActionAccelerate: Failed to find operating point after Overload");
							}
							DriverAcceleration = nextOperatingPoint.Acceleration;
							retVal = NextComponent.Request(absTime, nextOperatingPoint.SimulationInterval,
								nextOperatingPoint.Acceleration, gradient, false);
							if (retVal is ResponseFailTimeInterval rt)
								// occurs only with AT gearboxes - extend time interval after gearshift!
								retVal = new ResponseDrivingCycleDistanceExceeded(this) {
									MaxDistance = DriverAcceleration / 2 * rt.DeltaT * rt.DeltaT + DataBus.VehicleInfo.VehicleSpeed * rt.DeltaT
								};
						} else {
							if (absTime > 0 && DataBus.VehicleInfo.VehicleStopped) {
								Log.Info(
									"Operating point with limited acceleration resulted in an overload! Vehicle stopped! trying HALT action {0}",
									nextOperatingPoint.Acceleration);
								DataBus.Brakes.BrakePower = 1.SI<Watt>();
								retVal = DrivingActionHalt(absTime, nextOperatingPoint.SimulationInterval, 0.SI<MeterPerSecond>(), gradient);
								ds = 0.SI<Meter>();
								//retVal.Acceleration = 0.SI<MeterPerSquareSecond>();
							} else {
								if (response is ResponseEngineSpeedTooHigh) {
									Log.Info("Operating point with limited acceleration due to high engine speed resulted in an overload, searching again...");
									nextOperatingPoint = SearchOperatingPoint(absTime, ds, gradient, operatingPoint.Acceleration, retVal);
									DriverAcceleration = nextOperatingPoint.Acceleration;
									retVal = NextComponent.Request(absTime, nextOperatingPoint.SimulationInterval,
										nextOperatingPoint.Acceleration, gradient, false);
								} else {
									Log.Info("Operating point with limited acceleration resulted in an overload! trying again with original acceleration {0}",
										nextOperatingPoint.Acceleration);
									DriverAcceleration = nextOperatingPoint.Acceleration;
									retVal = NextComponent.Request(absTime, nextOperatingPoint.SimulationInterval,
										nextOperatingPoint.Acceleration, gradient, false);
								}
							}
						}
						retVal.Driver.Acceleration = operatingPoint.Acceleration;
						switch (retVal) {
							case ResponseDrivingCycleDistanceExceeded _: break;
							case ResponseSuccess _:
								operatingPoint = nextOperatingPoint;
								break;
							case ResponseGearShift _:
								operatingPoint = nextOperatingPoint;
								break;
							case ResponseOverload r:
								nextOperatingPoint = SearchOperatingPoint(absTime, ds, gradient, operatingPoint.Acceleration, r);
								DriverAcceleration = nextOperatingPoint.Acceleration;
								retVal = NextComponent.Request(absTime, nextOperatingPoint.SimulationInterval,
									nextOperatingPoint.Acceleration, gradient, false);
								if (retVal is ResponseFailTimeInterval rt)
									// occurs only with AT gearboxes - extend time interval after gearshift!
									retVal = new ResponseDrivingCycleDistanceExceeded(this) {
										MaxDistance = DriverAcceleration / 2 * rt.DeltaT * rt.DeltaT + DataBus.VehicleInfo.VehicleSpeed * rt.DeltaT
									};
								break;
							case ResponseFailTimeInterval r:
								// occurs only with AT gearboxes - extend time interval after gearshift!
								retVal = new ResponseDrivingCycleDistanceExceeded(this) {
									MaxDistance = r.Driver.Acceleration / 2 * r.DeltaT * r.DeltaT + DataBus.VehicleInfo.VehicleSpeed * r.DeltaT
								};
								break;
							case ResponseBatteryEmpty _:
								return retVal;
							default:
								throw new UnexpectedResponseException("DrivingAction Accelerate after Overload", retVal);
						}

						break;
					case ResponseGearShift _:
						operatingPoint = limitedOperatingPoint;
						break;
					case ResponseFailTimeInterval r:
						// occurs only with AT gearboxes - extend time interval after gearshift!
						retVal = new ResponseDrivingCycleDistanceExceeded(this) {
							MaxDistance = r.Driver.Acceleration / 2 * r.DeltaT * r.DeltaT + DataBus.VehicleInfo.VehicleSpeed * r.DeltaT
						};
						break;
					case ResponseSuccess _:
						operatingPoint = limitedOperatingPoint;
						break;
					case ResponseBatteryEmpty _:
						return retVal;
					case ResponseEngineSpeedTooHigh r:
						nextOperatingPoint = SearchOperatingPoint(absTime, ds, gradient, operatingPoint.Acceleration, r);
						retVal = NextComponent.Request(absTime, nextOperatingPoint.SimulationInterval, nextOperatingPoint.Acceleration, gradient, false);
						break;
					default:
						throw new UnexpectedResponseException("DrivingAction Accelerate after SearchOperatingPoint.", retVal);
				}
			}

			CurrentState.Acceleration = operatingPoint.Acceleration;
			CurrentState.dt = operatingPoint.SimulationInterval;
			CurrentState.Response = retVal;

			retVal.Driver.Acceleration = operatingPoint.Acceleration;
			retVal.SimulationInterval = operatingPoint.SimulationInterval;
			retVal.SimulationDistance = ds;
			retVal.Driver.OperatingPoint = operatingPoint;

			return retVal;
		}

		/// <summary>
		/// see documentation of IDriverActions
		/// </summary>
		/// <param name="absTime"></param>
		/// <param name="ds"></param>
		/// <param name="maxVelocity"></param>
		/// <param name="gradient"></param>
		/// <returns></returns>
		public IResponse DrivingActionCoast(Second absTime, Meter ds, MeterPerSecond maxVelocity, Radian gradient)
		{
			DrivingAction = DrivingAction.Coast;
			IterationStatistics.Increment(this, "Coast");
			Log.Debug("DrivingAction Coast");

			var gear = DataBus.GearboxInfo().Gear;
			var tcLocked = DataBus.GearboxInfo().TCLocked;
			var retVal = CoastOrRollAction(absTime, ds, maxVelocity, gradient, false);
			var gearChanged = !(DataBus.GearboxInfo().Gear == gear && DataBus.GearboxInfo().TCLocked == tcLocked);
			if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission()
				&& gearChanged
				&& (retVal is ResponseOverload || retVal is ResponseUnderload)) {
				Log.Debug("Gear changed after a valid operating point was found - re-try coasting!");
				retVal = CoastOrRollAction(absTime, ds, maxVelocity, gradient, false);
			}

			return retVal;
		}

		/// <summary>
		/// see documentation of IDriverActions
		/// </summary>
		/// <param name="absTime"></param>
		/// <param name="ds"></param>
		/// <param name="maxVelocity"></param>
		/// <param name="gradient"></param>
		/// <returns></returns>
		public IResponse DrivingActionRoll(Second absTime, Meter ds, MeterPerSecond maxVelocity, Radian gradient)
		{
			DrivingAction = DrivingAction.Roll;
			IterationStatistics.Increment(this, "Roll");

			Log.Debug("DrivingAction Roll");

			var retVal = CoastOrRollAction(absTime, ds, maxVelocity, gradient, true);
			if (retVal is ResponseGearShift)
				throw new UnexpectedResponseException("DrivingAction Roll: Gearshift during Roll action.", retVal);

			return retVal;
		}

		/// <summary>
		/// 
		/// </summary>
		/// <param name="absTime"></param>
		/// <param name="ds"></param>
		/// <param name="maxVelocity"></param>
		/// <param name="gradient"></param>
		/// <param name="rollAction"></param>
		/// <returns>
		/// * ResponseSuccess
		/// * ResponseDrivingCycleDistanceExceeded: vehicle is at low speed, coasting would lead to stop before ds is reached.
		/// * ResponseSpeedLimitExceeded: vehicle accelerates during coasting which would lead to exceeding the given maxVelocity (e.g., driving downhill, engine's drag load is not sufficient)
		/// * ResponseUnderload: engine's operating point is below drag curve (vehicle accelerates more than driver model allows; engine's drag load is not sufficient for limited acceleration
		/// * ResponseGearShift: gearbox needs to shift gears, vehicle can not accelerate (traction interruption)
		/// * ResponseFailTimeInterval: 
		/// </returns>
		protected IResponse CoastOrRollAction(Second absTime, Meter ds, MeterPerSecond maxVelocity, Radian gradient,
			bool rollAction)
		{
			var requestedOperatingPoint = ComputeAcceleration(ds, DataBus.VehicleInfo.VehicleSpeed);
			DriverAcceleration = requestedOperatingPoint.Acceleration;
			var initialResponse = NextComponent.Request(absTime, requestedOperatingPoint.SimulationInterval,
				requestedOperatingPoint.Acceleration, gradient, dryRun: true);

			OperatingPoint searchedOperatingPoint;
			try {
				searchedOperatingPoint = SearchOperatingPoint(
					absTime, requestedOperatingPoint.SimulationDistance,
					gradient,
					requestedOperatingPoint.Acceleration, initialResponse, coastingOrRoll: true);
			} catch (VectoEngineSpeedTooLowException) {
				// in case of an exception during search the engine-speed got too low - gear disengaged --> try again with disengaged gear.
				searchedOperatingPoint = SearchOperatingPoint(
					absTime, requestedOperatingPoint.SimulationDistance,
					gradient,
					requestedOperatingPoint.Acceleration, initialResponse, coastingOrRoll: true);
			}

			var tcOperatingPointSet = false;
			if (searchedOperatingPoint == null && DataBus.GearboxInfo().GearboxType.AutomaticTransmission()) {
				// we end up here if no valid operating point for the engine and torque converter can be found.
				// a likely reason is that the torque converter opereating point 'jumps' between two different operating points
				// or that no valid operating point can be found by reverse calcualtion. This method is a kind of fal-back
				// solution where a torque converter operating point is searched by forward calculation first and then the remaining
				// powertrain is adjusted to this operating point.
				searchedOperatingPoint = SetTCOperatingPointATGbxCoastOrRoll(absTime, gradient, requestedOperatingPoint, initialResponse as ResponseDryRun);
				tcOperatingPointSet = true;
			}

			if (searchedOperatingPoint == null) {
				searchedOperatingPoint = SearchOperatingPoint(
					absTime, requestedOperatingPoint.SimulationDistance,
					gradient,
					requestedOperatingPoint.Acceleration, initialResponse, coastingOrRoll: true, allowDistanceDecrease: true);
				if (searchedOperatingPoint == null) {
					throw new NotImplementedException();
				}

				if (searchedOperatingPoint.SimulationDistance.IsSmaller(ds)) {
					return new ResponseDrivingCycleDistanceExceeded(this) {
						MaxDistance = searchedOperatingPoint.SimulationDistance
					};
				}
			}

			if (!ds.IsEqual(searchedOperatingPoint.SimulationDistance)) {
				// vehicle is at low speed, coasting would lead to stop before ds is reached: reduce simulated distance to stop distance.
				Log.Debug(
					"SearchOperatingPoint reduced the max. distance: {0} -> {1}. Issue new request from driving cycle!",
					searchedOperatingPoint.SimulationDistance, ds);
				CurrentState.Response = new ResponseDrivingCycleDistanceExceeded(this) {
					MaxDistance = searchedOperatingPoint.SimulationDistance,
					Driver = {
						Acceleration = searchedOperatingPoint.Acceleration,
						OperatingPoint = searchedOperatingPoint
						},
					SimulationInterval = searchedOperatingPoint.SimulationInterval
				};
				return CurrentState.Response;
			}

			Log.Debug("Found operating point for {2}. dt: {0}, acceleration: {1}",
				searchedOperatingPoint.SimulationInterval,
				searchedOperatingPoint.Acceleration, rollAction ? "ROLL" : "COAST");

			var ignoreDriverLimits = rollAction || tcOperatingPointSet;

			var limitedOperatingPoint = LimitAccelerationByDriverModel(searchedOperatingPoint,
				ignoreDriverLimits ? LimitationMode.NoLimitation : LimitationMode.LimitDecelerationDriver);

			// compute speed at the end of the simulation interval. if it exceeds the limit -> return
			var v2 = DataBus.VehicleInfo.VehicleSpeed +
					limitedOperatingPoint.Acceleration * limitedOperatingPoint.SimulationInterval;
			if (v2 > maxVelocity && limitedOperatingPoint.Acceleration.IsGreaterOrEqual(0)) {
				Log.Debug("vehicle's velocity would exceed given max speed. v2: {0}, max speed: {1}", v2, maxVelocity);
				return new ResponseSpeedLimitExceeded(this);
			}

			DriverAcceleration = limitedOperatingPoint.Acceleration;
			var response = NextComponent.Request(absTime, limitedOperatingPoint.SimulationInterval,
				limitedOperatingPoint.Acceleration, gradient, false);

			response.SimulationInterval = limitedOperatingPoint.SimulationInterval;
			response.SimulationDistance = ds;
			response.Driver.Acceleration = limitedOperatingPoint.Acceleration;
			response.Driver.OperatingPoint = limitedOperatingPoint;

			switch (response) {
				case ResponseSuccess _:
				case ResponseUnderload _: // driver limits acceleration, operating point may be below engine's drag load resp. below 0
				case ResponseOverload _: // driver limits acceleration, operating point may be above 0 (GBX), use brakes
				case ResponseEngineSpeedTooHigh _: // reduce acceleration/vehicle speed
				case ResponseGearShift _:
					break;
				case ResponseFailTimeInterval r:
					response = new ResponseDrivingCycleDistanceExceeded(this) {
						MaxDistance = r.Driver.Acceleration / 2 * r.DeltaT * r.DeltaT + DataBus.VehicleInfo.VehicleSpeed * r.DeltaT
					};
					break;
				case ResponseBatteryEmpty _:
					return response;
				default:
					throw new UnexpectedResponseException("CoastOrRoll Action: unhandled response from powertrain.", response);
			}

			CurrentState.Response = response;
			CurrentState.Acceleration = response.Driver.Acceleration;
			CurrentState.dt = response.SimulationInterval;
			return response;
		}

		// Fallback solution for calculating operating point with TC in semi-forward way.
		private OperatingPoint SetTCOperatingPointATGbxCoastOrRoll(Second absTime, Radian gradient, OperatingPoint operatingPoint, ResponseDryRun dryRunResp)
		{
			var tc = DataBus.TorqueConverterCtl();
			var tcInfo = DataBus.TorqueConverterInfo();
			if (tc == null) {
				throw new VectoException("NO TorqueConverter Available!");
			}

			if (dryRunResp == null) {
				throw new VectoException("dry-run response expected!");
			}


			// first attempt: set TC to an input speed slightly above idle speed
			// calculate TC opPt using n_in and n_out, estimate ICE max and drag torque.
			// if ICE torque is within valid range, search an acceleration that results in the required 
			// out-torque at the torque converter
			var engineSpeed = DataBus.EngineInfo.EngineIdleSpeed * 1.01;
			var tcOp = EstimateTCOpPoint(operatingPoint, dryRunResp, engineSpeed, tcInfo);

			if (tcOp.Item1.Item2.IsBetween(tcOp.Item2, tcOp.Item3)) {
				if (!dryRunResp.TorqueConverter.TorqueConverterOperatingPoint.OutTorque.IsEqual(tcOp.Item1.Item1.OutTorque)) {
					tc.SetOperatingPoint = tcOp.Item1.Item1;
				}
				try {
					var acceleration = SearchAccelerationFixedTC(absTime, gradient, operatingPoint, tcOp.Item1, dryRunResp);
					return ComputeTimeInterval(acceleration, operatingPoint.SimulationDistance);
				} catch (Exception e) {
					Log.Error(e, "Failed to find acceleration for tc operating point! absTime: {0}", absTime);
					throw;
				}
			}

			// try again without changing the engine speed to 'spare' inertia torque
			engineSpeed = DataBus.EngineInfo.EngineSpeed;
			tcOp = EstimateTCOpPoint(operatingPoint, dryRunResp, engineSpeed, tcInfo);

			if (tcOp.Item1.Item2.IsBetween(tcOp.Item2, tcOp.Item3)) {
				if (!dryRunResp.TorqueConverter.TorqueConverterOperatingPoint.OutTorque.IsEqual(tcOp.Item1.Item1.OutTorque)) {
					tc.SetOperatingPoint = tcOp.Item1.Item1;
				}
				try {
					var acceleration = SearchAccelerationFixedTC(absTime, gradient, operatingPoint, tcOp.Item1, dryRunResp);
					return ComputeTimeInterval(acceleration, operatingPoint.SimulationDistance);
				} catch (Exception e) {
					Log.Error(e, "Failed to find acceleration for tc operating point! absTime: {0}", absTime);
					throw;
				}
			}

			// Attempt 2: search for an input speed (ICE speed) so that a valid operating point for 
			// the torque converter and the engine are found. Estimate max torque, drag torque. calculate delta
			// based on over-/underload of torque and too high or too low engine speed
			PerSecond nextICESpeed;
			try {
				nextICESpeed = SearchAlgorithm.Search(
					engineSpeed, GetTCDelta(tcOp.Item1, tcOp.Item2, tcOp.Item3), engineSpeed * 0.1,
					getYValue: tOp => {
						var t = (Tuple<Tuple<TorqueConverterOperatingPoint, NewtonMeter>, NewtonMeter, NewtonMeter>)tOp;
						return GetTCDelta(t.Item1, t.Item2, t.Item3);
					},
					evaluateFunction: engSpeed => EstimateTCOpPoint(operatingPoint, dryRunResp, engSpeed, tcInfo),
					criterion: tOp => {
						var t = (Tuple<Tuple<TorqueConverterOperatingPoint, NewtonMeter>, NewtonMeter, NewtonMeter>)tOp;
						return GetTCDelta(t.Item1, t.Item2, t.Item3).Value();
					},
					searcher: this);
			} catch (Exception e) {
				Log.Error(e, "Failed to find engine speed for valid torque converter operating point! absTime: {0}", absTime);

				// if no engine speed can be found that results in an operating point on the TC curve, set the TC in-torque to the maximum
				// available from the engine. reverse-calc TC-in-torque from average engine torque 
				var tcInPwrPrev = (DataBus.EngineInfo.EngineSpeed + tcOp.Item1.Item1.InAngularVelocity) * tcOp.Item1.Item2 -
								(tcOp.Item1.Item1.InAngularVelocity * tcOp.Item1.Item1.InTorque);
				tcOp.Item1.Item1.InTorque = (2 * tcOp.Item3 * tcOp.Item1.Item1.InAngularVelocity - tcInPwrPrev) /
											tcOp.Item1.Item1.InAngularVelocity;
				tc.SetOperatingPoint = tcOp.Item1.Item1;
				var acceleration = SearchAccelerationFixedTC(absTime, gradient, operatingPoint, tcOp.Item1, dryRunResp);

				return ComputeTimeInterval(acceleration, operatingPoint.SimulationDistance);
			}

			// a suitable engine sped was found - search acceleration to match TC out-torque
			try {
				tcOp = EstimateTCOpPoint(operatingPoint, dryRunResp, nextICESpeed, tcInfo);
				tc.SetOperatingPoint = tcOp.Item1.Item1;

				var acceleration = SearchAccelerationFixedTC(absTime, gradient, operatingPoint, tcOp.Item1, dryRunResp);

				return ComputeTimeInterval(acceleration, operatingPoint.SimulationDistance);
			} catch (Exception e) {
				Log.Error(e, "Failed to find acceleration for tc operating point! absTime: {0}", absTime);
				throw;
			}

			//return null;
		}

		// estimate a torque converter operating point via forward calculation for a certain engine speed. 
		// furthermore, estimates the max/min torque at ICE out-shaft including estimates for ICE inertia & aux torque
		private Tuple<Tuple<TorqueConverterOperatingPoint, NewtonMeter>, NewtonMeter, NewtonMeter> EstimateTCOpPoint(
			OperatingPoint operatingPoint, IResponse response, PerSecond engSpeed, ITorqueConverterInfo tc)
		{
			var avgICDSpeed = (DataBus.EngineInfo.EngineSpeed + engSpeed) / 2.0;
			var drTq = (DataBus.EngineInfo.EngineDragPower(avgICDSpeed)) / avgICDSpeed;
			var maxTq = DataBus.EngineInfo.EngineDynamicFullLoadPower(avgICDSpeed, operatingPoint.SimulationInterval) /
						avgICDSpeed * 0.995;
			var inTq = Formulas.InertiaPower(
							engSpeed, DataBus.EngineInfo.EngineSpeed,
							(DataBus as VehicleContainer)?.RunData.EngineData.Inertia ?? 0.SI<KilogramSquareMeter>(),
							operatingPoint.SimulationInterval) / avgICDSpeed;
			var auxTq = DataBus.EngineInfo.EngineAuxDemand(avgICDSpeed, operatingPoint.SimulationInterval) / avgICDSpeed;

			return Tuple.Create(
				tc.CalculateOperatingPoint(engSpeed, response.Gearbox.InputSpeed), drTq - inTq - auxTq, maxTq - inTq - auxTq);
		}


		// Search vehicle acceleration to match the torque converter out-torque for a fixed TC opPt
		private MeterPerSquareSecond SearchAccelerationFixedTC(
			Second absTime, Radian gradient, OperatingPoint operatingPoint, Tuple<TorqueConverterOperatingPoint, NewtonMeter> tcOp, ResponseDryRun dryRun)
		{
			var acceleration = SearchAlgorithm.Search(
				operatingPoint.Acceleration, tcOp.Item1.OutTorque - dryRun.TorqueConverter.TorqueConverterTorqueDemand,
				Constants.SimulationSettings.OperatingPointInitialSearchIntervalAccelerating,
				getYValue: resp => {
					var r = (ResponseDryRun)resp;
					return tcOp.Item1.OutTorque - r.TorqueConverter.TorqueConverterTorqueDemand;
				},
				evaluateFunction:
				acc => {
					var tmp = ComputeTimeInterval(acc, operatingPoint.SimulationDistance);
					if (tmp.SimulationInterval.IsEqual(0.SI<Second>(), 1e-9.SI<Second>())) {
						throw new VectoSearchAbortedException(
							"next TimeInterval is 0. a: {0}, v: {1}, dt: {2}", acc,
							DataBus.VehicleInfo.VehicleSpeed, tmp.SimulationInterval);
					}

					DriverAcceleration = acc;
					var tmpResponse = NextComponent.Request(absTime, tmp.SimulationInterval, acc, gradient, true);
					tmpResponse.Driver.OperatingPoint = tmp;
					return tmpResponse;
				},
				criterion: resp => {
					var r = (ResponseDryRun)resp;

					return (tcOp.Item1.OutTorque - r.TorqueConverter.TorqueConverterTorqueDemand).Value();
				},
				searcher: this
			);
			return acceleration;
		}

		private NewtonMeter GetTCDelta(Tuple<TorqueConverterOperatingPoint, NewtonMeter> tqOp, NewtonMeter dragTorque, NewtonMeter maxTorque)
		{
			var deltaSpeed = VectoMath.Min(0.RPMtoRad(), tqOp.Item1.InAngularVelocity - DataBus.EngineInfo.EngineIdleSpeed) +
							VectoMath.Max(0.RPMtoRad(), tqOp.Item1.InAngularVelocity - DataBus.EngineInfo.EngineRatedSpeed);
			var tqDiff = 0.SI<NewtonMeter>();
			if (tqOp.Item2.IsSmaller(dragTorque)) {
				tqDiff = tqOp.Item2 - dragTorque;
			}

			if (tqOp.Item2.IsGreater(maxTorque)) {
				tqDiff = tqOp.Item2 - maxTorque;
			}
			return (tqDiff.Value() * tqDiff.Value() + deltaSpeed.Value() * deltaSpeed.Value()).SI<NewtonMeter>();

		}

		public IResponse DrivingActionBrake(Second absTime, Meter ds, MeterPerSecond nextTargetSpeed, Radian gradient, IResponse previousResponse = null, Meter targetDistance = null, DrivingAction? overrideAction = null)
		{
			DrivingAction = overrideAction ?? DrivingAction.Brake;
			IterationStatistics.Increment(this, "Brake");
			Log.Debug("DrivingAction Brake");

			IResponse retVal = null;

			var op1 = ComputeAcceleration(ds, nextTargetSpeed);

			//if (operatingPoint.Acceleration.IsSmaller(0)) {
			var op2 = IncreaseDecelerationToMaxWithinSpeedRange(op1);

			var operatingPoint =
				AdaptDecelerationToTargetDistance(ds, nextTargetSpeed, targetDistance, op2.Acceleration) ??
				op2;

			DriverAcceleration = operatingPoint.Acceleration;
			var response = !smartBusAux && previousResponse != null
				? previousResponse
				: NextComponent.Request(
					absTime, operatingPoint.SimulationInterval, operatingPoint.Acceleration,
					gradient, false);

			var point = operatingPoint;
			switch (response) {
				case ResponseSuccess r:
					retVal = r;
					break;
				case ResponseOverload r:
					retVal = r;
					break; // i.e., driving uphill, clutch open, deceleration higher than desired deceleration
				case ResponseUnderload _:
					break; // will be handled in SearchBrakingPower
				case ResponseEngineSpeedTooHigh r:
					Log.Debug("Engine speed was too high, search for appropriate acceleration first.");
					operatingPoint = SearchOperatingPoint(absTime, ds, gradient, point.Acceleration, response);
					break; // will be handled in SearchBrakingPower
				case ResponseGearShift _:
					break; // will be handled in SearchBrakingPower
				case ResponseFailTimeInterval r:
					retVal = new ResponseDrivingCycleDistanceExceeded(this) {
						MaxDistance = DataBus.VehicleInfo.VehicleSpeed * r.DeltaT + point.Acceleration / 2 * r.DeltaT * r.DeltaT
					};
					break;
				case ResponseBatteryEmpty _:
					return response;
				default:
					throw new UnexpectedResponseException("DrivingAction Brake: first request.", response);
			}

			if (retVal != null) {
				CurrentState.Acceleration = operatingPoint.Acceleration;
				CurrentState.dt = operatingPoint.SimulationInterval;
				CurrentState.Response = retVal;
				retVal.Driver.Acceleration = operatingPoint.Acceleration;
				retVal.SimulationInterval = operatingPoint.SimulationInterval;
				retVal.SimulationDistance = ds;
				retVal.Driver.OperatingPoint = operatingPoint;
				return retVal;
			}

			var engaged = DataBus.GearboxInfo().DisengageGearbox;
			try {
				operatingPoint = SearchBrakingPower(
					absTime, operatingPoint.SimulationDistance, gradient,
					operatingPoint.Acceleration, response);
			} catch (VectoSearchAbortedException vsa) {
				Log.Warn("Search braking power aborted {0}", vsa);
				if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission()) {
					operatingPoint = SetTCOperatingPointATGbxBraking(absTime, gradient, operatingPoint, response);
				}
			}
			if (!ds.IsEqual(operatingPoint.SimulationDistance, 1E-15.SI<Meter>())) {
				Log.Info(
					"SearchOperatingPoint Braking reduced the max. distance: {0} -> {1}. Issue new request from driving cycle!",
					operatingPoint.SimulationDistance, ds);
				return new ResponseDrivingCycleDistanceExceeded(this) {
					MaxDistance = operatingPoint.SimulationDistance
				};
			}

			Log.Debug("Found operating point for braking. dt: {0}, acceleration: {1} brakingPower: {2}",
				operatingPoint.SimulationInterval,
				operatingPoint.Acceleration, DataBus.Brakes.BrakePower);
			if (DataBus.Brakes.BrakePower < 0) {
				var overload = new ResponseOverload(this) {
					Brakes = { BrakePower = DataBus.Brakes.BrakePower, },
					Driver = { Acceleration = operatingPoint.Acceleration }
				};
				DataBus.Brakes.BrakePower = 0.SI<Watt>();
				return overload;
			}

			DriverAcceleration = operatingPoint.Acceleration;
			var gear = DataBus.GearboxInfo().Gear;
			var tcLocked = DataBus.GearboxInfo().TCLocked;
			retVal = NextComponent.Request(absTime, operatingPoint.SimulationInterval, operatingPoint.Acceleration,
				gradient, false);
			var gearChanged = !(DataBus.GearboxInfo().Gear == gear && DataBus.GearboxInfo().TCLocked == tcLocked);
			if ((DataBus.GearboxInfo().GearboxType.AutomaticTransmission() || DataBus.HybridControllerInfo != null)
				&& gearChanged
				&& (retVal is ResponseOverload || retVal is ResponseUnderload)) {
				Log.Debug("Gear changed after a valid operating point was found - braking is no longer applicable due to overload");
				return null;
			}

			if (DataBus.HybridControllerCtl != null && response is ResponseEngineSpeedTooHigh &&
				!(retVal is ResponseSuccess)) {
				// search brakingpower found a solution but request resulted in non-success - try again
				DataBus.Brakes.BrakePower = 0.SI<Watt>();
				try {
					operatingPoint = SearchBrakingPower(
						absTime, operatingPoint.SimulationDistance, gradient,
						operatingPoint.Acceleration, response);
				} catch (VectoSearchAbortedException vsa) {
					Log.Warn("Search braking power aborted {0}", vsa);
					if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission()) {
						operatingPoint = SetTCOperatingPointATGbxBraking(absTime, gradient, operatingPoint, response);
					}
				}
				retVal = NextComponent.Request(absTime, operatingPoint.SimulationInterval, operatingPoint.Acceleration,
					gradient, false);
			}

			switch (retVal) {
				case ResponseSuccess _: break;
				case ResponseGearShift _: break;
				case ResponseFailTimeInterval r:
					retVal = new ResponseDrivingCycleDistanceExceeded(this) {
						MaxDistance = DataBus.VehicleInfo.VehicleSpeed * r.DeltaT + operatingPoint.Acceleration / 2 * r.DeltaT * r.DeltaT
					};
					break;
				case ResponseUnderload r:
					if (DataBus.HybridControllerInfo != null) {
						DrivingAction = DrivingAction.Brake;
					}
					if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission() || DataBus.GearboxInfo().GearboxType == GearboxType.APTN) {
						operatingPoint = SearchBrakingPower(absTime, operatingPoint.SimulationDistance, gradient,
							operatingPoint.Acceleration, response);
						DriverAcceleration = operatingPoint.Acceleration;
						retVal = NextComponent.Request(absTime, operatingPoint.SimulationInterval,
							operatingPoint.Acceleration, gradient, false);
					}
					break;
				case ResponseOverload r:
					if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission()) {
						// overload may happen because of gearshift between search and actual request, search again
						var i = 5;
						while (i-- > 0 && !(retVal is ResponseSuccess)) {
							DataBus.Brakes.BrakePower = 0.SI<Watt>();

							retVal = NextComponent.Request(
								absTime, operatingPoint.SimulationInterval, operatingPoint.Acceleration,
								gradient, false);
							if (retVal is ResponseSuccess) {
								break;
							}

							try {
								operatingPoint = SearchBrakingPower(absTime, operatingPoint.SimulationDistance,
									gradient,
									operatingPoint.Acceleration, retVal);
							} catch (VectoSearchAbortedException vsa) {
								Log.Warn("Search braking power aborted {0}", vsa);
								if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission()) {
									operatingPoint = SetTCOperatingPointATGbxBraking(absTime, gradient, operatingPoint,
										response);
								}
							}

							DriverAcceleration = operatingPoint.Acceleration;
							if (DataBus.Brakes.BrakePower.IsSmaller(0)) {
								DataBus.Brakes.BrakePower = 0.SI<Watt>();

								operatingPoint = SearchOperatingPoint(absTime, ds, gradient, 0.SI<MeterPerSquareSecond>(), r);
							}
							retVal = NextComponent.Request(absTime, operatingPoint.SimulationInterval,
								operatingPoint.Acceleration, gradient, false);
						}
					} else {
						throw new UnexpectedResponseException(
							"DrivingAction Brake: request failed after braking power was found.", r);
					}

					break;
				case ResponseBatteryEmpty _:
					return retVal;
				default:
					throw new UnexpectedResponseException("DrivingAction Brake: request failed after braking power was found.", retVal);
			}

			CurrentState.Acceleration = operatingPoint.Acceleration;
			CurrentState.dt = operatingPoint.SimulationInterval;
			CurrentState.Response = retVal;
			retVal.Driver.Acceleration = operatingPoint.Acceleration;
			retVal.SimulationInterval = operatingPoint.SimulationInterval;
			retVal.SimulationDistance = ds;
			retVal.Driver.OperatingPoint = operatingPoint;

			if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission() && engaged != DataBus.GearboxInfo().DisengageGearbox) {
				DataBus.GearboxCtl().DisengageGearbox = engaged;
			}
			return retVal;
		}

		private OperatingPoint SetTCOperatingPointATGbxBraking(
			Second absTime, Radian gradient, OperatingPoint operatingPoint, IResponse response)
		{
			var tc = DataBus.TorqueConverterCtl();
			if (tc == null) {
				throw new VectoException("NO TorqueConverter Available!");
			}

			var avgEngineSpeed = (DataBus.EngineInfo.EngineSpeed + DataBus.EngineInfo.EngineIdleSpeed) / 2.0;
			var dragTorque = (DataBus.EngineInfo.EngineDragPower(avgEngineSpeed)) / avgEngineSpeed;
			var maxTorque = DataBus.EngineInfo.EngineDynamicFullLoadPower(avgEngineSpeed, operatingPoint.SimulationInterval) / avgEngineSpeed;
			var inertiaTq = Formulas.InertiaPower(
								DataBus.EngineInfo.EngineIdleSpeed, DataBus.EngineInfo.EngineSpeed,
								(DataBus as VehicleContainer)?.RunData.EngineData.Inertia ?? 0.SI<KilogramSquareMeter>(),
								operatingPoint.SimulationInterval) / avgEngineSpeed;
			var auxTqDemand = DataBus.EngineInfo.EngineAuxDemand(avgEngineSpeed, operatingPoint.SimulationInterval) / avgEngineSpeed;
			//var maxTorque = DataBus.e
			var tcOp = DataBus.TorqueConverterInfo().CalculateOperatingPoint(DataBus.EngineInfo.EngineIdleSpeed * 1.01, response.Gearbox.InputSpeed);

			//if (tcOp.Item2.IsBetween(dragTorque - inertiaTq - auxTqDemand, maxTorque - inertiaTq - auxTqDemand)) {
				_previousGearboxDisengaged = DataBus.GearboxInfo().DisengageGearbox;
				DataBus.GearboxCtl().DisengageGearbox = true;
				operatingPoint = SearchBrakingPower(
					absTime, operatingPoint.SimulationDistance, gradient,
					operatingPoint.Acceleration, response);
				return operatingPoint;
			//}

			//return null;
		}

		private OperatingPoint AdaptDecelerationToTargetDistance(Meter ds, MeterPerSecond nextTargetSpeed,
			Meter targetDistance, MeterPerSquareSecond acceleration)
		{
			if (targetDistance != null && targetDistance > DataBus.MileageCounter.Distance) {
				var tmp = ComputeAcceleration(targetDistance - DataBus.MileageCounter.Distance, nextTargetSpeed, false);
				if (tmp.Acceleration.IsGreater(acceleration)) {
					var operatingPoint = ComputeTimeInterval(tmp.Acceleration, ds);
					if (!ds.IsEqual(operatingPoint.SimulationDistance)) {
						Log.Error("Unexpected Condition: Distance has been adjusted from {0} to {1}, currentVelocity: {2} acceleration: {3}, targetVelocity: {4}",
							operatingPoint.SimulationDistance, ds, DataBus.VehicleInfo.VehicleSpeed,
							operatingPoint.Acceleration, nextTargetSpeed);
						throw new VectoSimulationException("Simulation distance unexpectedly adjusted! {0} -> {1}", ds,
							operatingPoint.SimulationDistance);
					}
					return operatingPoint;
				}
			}
			return null;
		}

		private OperatingPoint IncreaseDecelerationToMaxWithinSpeedRange(OperatingPoint op)
		{
			var operatingPoint = new OperatingPoint(op);
			// if we should brake with the max. deceleration and the deceleration changes within the current interval, take the larger deceleration...
			if (operatingPoint.Acceleration.IsEqual(DriverData.AccelerationCurve.Lookup(DataBus.VehicleInfo.VehicleSpeed).Deceleration)) {
				var v2 = DataBus.VehicleInfo.VehicleSpeed + operatingPoint.Acceleration * operatingPoint.SimulationInterval;
				var nextAcceleration = DriverData.AccelerationCurve.Lookup(v2).Deceleration;
				var tmp = ComputeTimeInterval(VectoMath.Min(operatingPoint.Acceleration, nextAcceleration),
					operatingPoint.SimulationDistance);
				if (!operatingPoint.Acceleration.IsEqual(nextAcceleration) &&
					operatingPoint.SimulationDistance.IsEqual(tmp.SimulationDistance)) {
					// only adjust operating point if the acceleration is different but the simulation distance is not modified
					// i.e., braking to the next sample point (but a little bit slower)
					Log.Debug("adjusting acceleration from {0} to {1}", operatingPoint.Acceleration, tmp.Acceleration);
					operatingPoint = tmp;
					// ComputeTimeInterval((operatingPoint.Acceleration + tmp.Acceleration) / 2, operatingPoint.SimulationDistance);
				}
			}
			return operatingPoint;
		}

		// ================================================

		private OperatingPoint LimitAccelerationByDriverModel(OperatingPoint operatingPoint, LimitationMode limits)
		{
			var limitApplied = false;
			var retVal = new OperatingPoint(operatingPoint);

			var accelerationLimits = DriverData.AccelerationCurve.Lookup(DataBus.VehicleInfo.VehicleSpeed);

			if (limits != LimitationMode.NoLimitation && operatingPoint.Acceleration > accelerationLimits.Acceleration) {
				retVal.Acceleration = accelerationLimits.Acceleration;
				limitApplied = true;
			}

			if ((limits & LimitationMode.LimitDecelerationDriver) != 0
				&& retVal.Acceleration < accelerationLimits.Deceleration) {
				retVal.Acceleration = accelerationLimits.Deceleration;
				limitApplied = true;
			}

			if (limitApplied) {
				retVal.SimulationInterval =
					ComputeTimeInterval(retVal.Acceleration, retVal.SimulationDistance).SimulationInterval;
				Log.Debug("Limiting acceleration from {0} to {1}, dt: {2}", operatingPoint.Acceleration,
						retVal.Acceleration, retVal.SimulationInterval);
			}
			return retVal;
		}

		/// <summary>
		/// Performs a search for the required braking power such that the vehicle accelerates with the given acceleration.
		/// Returns a new operating point (a, ds, dt) where ds may be shorter due to vehicle stopping
		/// </summary>
		/// <returns>operating point (a, ds, dt) such that the vehicle accelerates with the given acceleration.</returns>
		private OperatingPoint SearchBrakingPower(Second absTime, Meter ds, Radian gradient,
			MeterPerSquareSecond acceleration, IResponse initialResponse)
		{
			IterationStatistics.Increment(this, "SearchBrakingPower", 0);

			var operatingPoint = new OperatingPoint { SimulationDistance = ds, Acceleration = acceleration };
			operatingPoint = ComputeTimeInterval(operatingPoint.Acceleration, ds);
			Watt deltaPower = null;
			switch (initialResponse) {
				case ResponseGearShift r:
					IterationStatistics.Increment(this, "SearchBrakingPower");
					DriverAcceleration = operatingPoint.Acceleration;
					var nextResp = NextComponent.Request(absTime, operatingPoint.SimulationInterval,
						operatingPoint.Acceleration, gradient, true);
					deltaPower = nextResp.Gearbox.PowerRequest;
					break;
				case ResponseEngineSpeedTooHigh r:
					IterationStatistics.Increment(this, "SearchBrakingPower");
					DriverAcceleration = operatingPoint.Acceleration;
					var nextResp1 = NextComponent.Request(absTime, operatingPoint.SimulationInterval,
						operatingPoint.Acceleration, gradient, true);

					deltaPower = DataBus.PowertrainInfo.HasGearbox ? nextResp1.Gearbox.PowerRequest : nextResp1.ElectricMotor.PowerRequest;/* ?? nextResp1.ElectricMotor.PowerRequest;*/
					break;
				case ResponseUnderload r:
					deltaPower = DataBus.ClutchInfo().ClutchClosed(absTime) && DataBus.GearboxInfo().GearEngaged(absTime) ? r.Delta : r.Gearbox.PowerRequest;
					break;
				default:
					throw new UnexpectedResponseException("cannot use response for searching braking power!", initialResponse);
			}

			try {
				var forceLineSearch = DataBus.GearboxInfo().GearboxType.AutomaticTransmission() && !DataBus.GearboxInfo().TCLocked;
				// in case we search for a braking power but the driver action is to accelerate (and we are in converter gear)
				// we do not need to search for an operating point at the ICE drag curve, take the first one where the ICE can operate
				// (as we use line-search and go stepwise up, this is fine)
				var takeFirstViableSolution =
					DataBus.DriverInfo.DrivingAction == DrivingAction.Accelerate && forceLineSearch;
				DataBus.Brakes.BrakePower = SearchAlgorithm.Search(DataBus.Brakes.BrakePower, deltaPower,
					deltaPower.Abs() * (DataBus.GearboxInfo().GearboxType.AutomaticTransmission() ? 0.5 : 1),
					getYValue: result => {
						var response = (ResponseDryRun)result;
						return DataBus.ClutchInfo().ClutchClosed(absTime)
								&& DataBus.GearboxInfo().GearEngaged(absTime) ? response.DeltaDragLoad : response.Gearbox.PowerRequest;
					},
					evaluateFunction: x => {
						DataBus.Brakes.BrakePower = x;
						operatingPoint = ComputeTimeInterval(operatingPoint.Acceleration, ds);

						IterationStatistics.Increment(this, "SearchBrakingPower");
						DriverAcceleration = operatingPoint.Acceleration;
						return NextComponent.Request(absTime, operatingPoint.SimulationInterval,
							operatingPoint.Acceleration, gradient,
							true);
					},
					criterion: result => {
						var response = (ResponseDryRun)result;
						if (takeFirstViableSolution && !(response.TorqueConverter?.TorqueConverterOperatingPoint?.Creeping ?? true)) {
							var engRes = response.Engine;
							var deltaFull = engRes.TotalTorqueDemand - engRes.DynamicFullLoadTorque;
							var deltaDrag = engRes.TotalTorqueDemand - engRes.DragTorque;
							var engineOK = deltaDrag.IsGreaterOrEqual(0) && deltaFull.IsSmallerOrEqual(0);
							if (engineOK) {
								return 0;
							}
						}
						var delta = DataBus.ClutchInfo().ClutchClosed(absTime) && DataBus.GearboxInfo().GearEngaged(absTime)
							? response.DeltaDragLoad * (forceLineSearch ? 1.1 : 1.0) // in case LineSearch is used, increase criteria to force more precision on the solution
							: response.Gearbox.PowerRequest;
						return delta.Value();
					},
					abortCriterion: (result, i) => {
						if (i < 7) {
							return false;
						}
						var response = (ResponseDryRun)result;
						if (response == null) {
							return false;
						}

						return DataBus.GearboxInfo().GearboxType.AutomaticTransmission() && response.DeltaDragLoad.Value().IsSmallerOrEqual(-double.MaxValue / 20);
					},
					forceLineSearch: forceLineSearch,
					searcher: this);

				return operatingPoint;
			} catch (VectoSearchFailedException vse) {
				Log.Error("Failed to find operating point for braking power! absTime: {0}  {1}", absTime, vse);
				if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission() && !DataBus.GearboxInfo().TCLocked) {
					// AT transmission in TC gear - maybe search failed because engine speed 'jumps' during
					// search and cannot reach drag curve
					// take an operating point that is 
					try {
						DataBus.Brakes.BrakePower = SearchAlgorithm.Search(DataBus.Brakes.BrakePower, deltaPower,
							DataBus.Brakes.BrakePower * 0.01,
							getYValue: result => {
								var response = (ResponseDryRun)result;
								return DataBus.ClutchInfo().ClutchClosed(absTime)
									? response.DeltaDragLoad
									: response.Gearbox.PowerRequest;
							},
							evaluateFunction: x => {
								DataBus.Brakes.BrakePower = x;
								operatingPoint = ComputeTimeInterval(operatingPoint.Acceleration, ds);

								IterationStatistics.Increment(this, "SearchBrakingPower");
								DriverAcceleration = operatingPoint.Acceleration;
								return NextComponent.Request(absTime, operatingPoint.SimulationInterval,
									operatingPoint.Acceleration, gradient,
									true);
							},
							criterion: result => {
								var response = (ResponseDryRun)result;
								var delta = DataBus.ClutchInfo().ClutchClosed(absTime)
									? response.DeltaDragLoad
									: response.Gearbox.PowerRequest;
								return Math.Min(delta.Value(), 0);
							},
							forceLineSearch: true,
							searcher: this);
						return operatingPoint;
					} catch (Exception e2) {
						Log.Error("Failed to find operating point for braking power (attempt 2)! absTime: {0}  {1}", absTime, e2);
						throw;
					}

				} else {
					throw;
				}
			} catch (Exception e) {
				Log.Error("Failed to find operating point for braking power! absTime: {0}  {1}", absTime, e);
				throw;
			}
		}

		protected OperatingPoint SearchOperatingPoint(Second absTime, Meter ds, Radian gradient,
			MeterPerSquareSecond acceleration, IResponse initialResponse, bool coastingOrRoll = false, bool allowDistanceDecrease = false)
		{
			IterationStatistics.Increment(this, "SearchOperatingPoint", 0);

			var retVal = new OperatingPoint { Acceleration = acceleration, SimulationDistance = ds };

			var actionRoll = !DataBus.ClutchInfo().ClutchClosed(absTime);

			var origDelta = GetOrigDelta(initialResponse, coastingOrRoll, actionRoll);

			var searchEngineSpeed = initialResponse is ResponseEngineSpeedTooHigh;

			var delta = origDelta;
			try {
				var nanCount = 0;
				retVal.Acceleration = SearchAlgorithm.Search(acceleration, delta,
					Constants.SimulationSettings.OperatingPointInitialSearchIntervalAccelerating,
					getYValue: response => {
						var r = (ResponseDryRun)response;
						if (searchEngineSpeed) {
							return (r.DeltaEngineSpeed + 1.RPMtoRad()) * 1.SI<NewtonMeter>();
						}
						return actionRoll ? r.Gearbox.PowerRequest : (coastingOrRoll ? r.DeltaDragLoad : r.DeltaFullLoad);
					},
					evaluateFunction:
						acc => {
							// calculate new time interval only when vehiclespeed and acceleration are != 0
							// else: use same timeinterval as before.
							var vehicleDrivesAndAccelerates = !(acc.IsEqual(0) && DataBus.VehicleInfo.VehicleSpeed.IsEqual(0));
							if (vehicleDrivesAndAccelerates) {
								var tmp = ComputeTimeInterval(acc, ds);
								if (tmp.SimulationInterval.IsEqual(0.SI<Second>(), 1e-9.SI<Second>())) {
									throw new VectoSearchAbortedException(
										"next TimeInterval is 0. a: {0}, v: {1}, dt: {2}", acc,
										DataBus.VehicleInfo.VehicleSpeed, tmp.SimulationInterval);
								}
								retVal.Acceleration = tmp.Acceleration;
								retVal.SimulationInterval = tmp.SimulationInterval;
								retVal.SimulationDistance = tmp.SimulationDistance;


							} else {
								retVal.Acceleration = acc;
								retVal.SimulationDistance = 0.SI<Meter>();
							}
							IterationStatistics.Increment(this, "SearchOperatingPoint");
							DriverAcceleration = acc;
							var response = NextComponent.Request(absTime, retVal.SimulationInterval, acc, gradient, true);
							response.Driver.OperatingPoint = retVal;
							return response;

						},
					criterion: response => {
						var r = (ResponseDryRun)response;
						if (searchEngineSpeed) return (r.DeltaEngineSpeed + 1.RPMtoRad()).Value();
						if (actionRoll) return r.Gearbox.PowerRequest.Value();
						if (coastingOrRoll) return r.DeltaDragLoad.Value();
						return r.DeltaFullLoad.Value();
					},
					abortCriterion:
						(response, cnt) => {
							var r = (ResponseDryRun)response;
							if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission()
								&& r.DeltaDragLoad.Value().IsSmallerOrEqual(-double.MaxValue / 20)
								&& coastingOrRoll
								&& !actionRoll) {
								nanCount++;
							}
							if (nanCount > 10) {
								return true;
							}
							return r != null && !actionRoll && !allowDistanceDecrease && !ds.IsEqual(r.Driver.OperatingPoint.SimulationDistance);
						},
					searcher: this);
				return ComputeTimeInterval(retVal.Acceleration, retVal.SimulationDistance);
			} catch (VectoException ve) {
				switch (ve) {
					case VectoSearchFailedException _:
					case VectoSearchAbortedException _:

						// search aborted, try to go ahead with the last acceleration
						if (!searchEngineSpeed && !actionRoll && !coastingOrRoll) {
							var nanCount1 = 0;
							try {
								retVal.Acceleration = SearchAlgorithm.Search(acceleration, delta,
									Constants.SimulationSettings.OperatingPointInitialSearchIntervalAccelerating,
									getYValue: response => ((ResponseDryRun)response).DeltaFullLoad,
									evaluateFunction:
									acc => {
										// calculate new time interval only when vehiclespeed and acceleration are != 0
										// else: use same timeinterval as before.
										var vehicleDrivesAndAccelerates =
											!(acc.IsEqual(0) && DataBus.VehicleInfo.VehicleSpeed.IsEqual(0));
										if (vehicleDrivesAndAccelerates) {
											var tmp = ComputeTimeInterval(acc, ds);
											if (tmp.SimulationInterval.IsEqual(0.SI<Second>(), 1e-9.SI<Second>())) {
												throw new VectoSearchAbortedException(
													"next TimeInterval is 0. a: {0}, v: {1}, dt: {2}", acc,
													DataBus.VehicleInfo.VehicleSpeed, tmp.SimulationInterval);
											}

											retVal.Acceleration = tmp.Acceleration;
											retVal.SimulationInterval = tmp.SimulationInterval;
											retVal.SimulationDistance = tmp.SimulationDistance;


										} else {
											retVal.Acceleration = acc;
											retVal.SimulationDistance = 0.SI<Meter>();
										}

										IterationStatistics.Increment(this, "SearchOperatingPoint");
										DriverAcceleration = acc;
										var response = NextComponent.Request(absTime, retVal.SimulationInterval, acc,
											gradient,
											true);
										response.Driver.OperatingPoint = retVal;
										return response;

									},
									criterion: response => {
										var r = (ResponseDryRun)response;

										delta = (r.DeltaFullLoad);
										return Math.Max(delta.Value(), 0);
									},
									abortCriterion:
									(response, cnt) => {
										var r = (ResponseDryRun)response;
										if (DataBus.GearboxInfo().GearboxType.AutomaticTransmission()
											&& r.DeltaDragLoad.Value().IsSmallerOrEqual(-double.MaxValue / 20)
											&& coastingOrRoll
											&& !actionRoll) {
											nanCount1++;
										}

										if (nanCount1 > 10) {
											return true;
										}

										return r != null && !allowDistanceDecrease &&
												!ds.IsEqual(r.Driver.OperatingPoint.SimulationDistance);
									},
									forceLineSearch: true,
									searcher: this);
								return ComputeTimeInterval(retVal.Acceleration, retVal.SimulationDistance);
							} catch (VectoException ve2) {
								Log.Error(ve2);
								return null;
							}
						}

						break;

				}
			} catch (Exception) {
				Log.Error("Failed to find operating point! absTime: {0}", absTime);
				throw;
			}

			if (!retVal.Acceleration.IsBetween(DriverData.AccelerationCurve.MaxDeceleration(),
				DriverData.AccelerationCurve.MaxAcceleration())) {
				Log.Info("Operating Point outside driver acceleration limits: a: {0}", retVal.Acceleration);
			}
			return null;
		}

		private static Watt GetOrigDelta(IResponse initialResponse, bool coastingOrRoll, bool actionRoll) {
			if (actionRoll) {
				switch (initialResponse) {
					case ResponseDryRun r: return r.Gearbox.PowerRequest;
					case ResponseOverload r: return r.Delta;
					case ResponseFailTimeInterval r: return r.Gearbox.PowerRequest;
					default: throw new UnexpectedResponseException("SearchOperatingPoint: Unknown response type.", initialResponse);
				}
			}

			switch (initialResponse) {
				case ResponseOverload r: return r.Delta;
				case ResponseEngineSpeedTooHigh r: return r.DeltaEngineSpeed * 1.SI<NewtonMeter>();
				case ResponseDryRun r: return coastingOrRoll ? r.DeltaDragLoad : r.DeltaFullLoad;
				default: throw new UnexpectedResponseException("SearchOperatingPoint: Unknown response type.", initialResponse);
			}
		}

		/// <summary>
		/// compute the acceleration and time-interval such that the vehicle's velocity approaches the given target velocity
		/// - first compute the acceleration to reach the targetVelocity within the given distance
		/// - limit the acceleration/deceleration by the driver's acceleration curve
		/// - compute the time interval required to drive the given distance with the computed acceleration
		/// computed acceleration and time interval are stored in CurrentState!
		/// </summary>
		/// <param name="ds">distance to reach the next target speed</param>
		/// <param name="targetVelocity">next vehicle speed to decelerate to</param>
		/// <param name="limitByDriverModel">if set to false the required acceleration will be computed, regardless of the driver's acceleration curve</param>
		public OperatingPoint ComputeAcceleration(Meter ds, MeterPerSecond targetVelocity,
			bool limitByDriverModel = true)
		{
			var currentSpeed = DataBus.VehicleInfo.VehicleSpeed;
			var retVal = new OperatingPoint() { SimulationDistance = ds };

			// Δx = (v0+v1)/2 * Δt
			// => Δt = 2*Δx/(v0+v1) 
			var dt = 2 * ds / (currentSpeed + targetVelocity);

			// a = Δv / Δt
			var requiredAcceleration = (targetVelocity - currentSpeed) / dt;

			if (!limitByDriverModel) {
				return ComputeTimeInterval(requiredAcceleration, ds);
			}

			var maxAcceleration = DriverData.AccelerationCurve.Lookup(currentSpeed);

			if (requiredAcceleration > maxAcceleration.Acceleration) {
				requiredAcceleration = maxAcceleration.Acceleration;
			}
			if (requiredAcceleration < maxAcceleration.Deceleration) {
				requiredAcceleration = maxAcceleration.Deceleration;
			}

			retVal.Acceleration = requiredAcceleration;
			retVal = ComputeTimeInterval(retVal.Acceleration, ds);

			if (ds.IsEqual(retVal.SimulationDistance)) {
				return retVal;
			}

			// this case should not happen, acceleration has been computed such that the target speed
			// can be reached within ds.
			Log.Error("Unexpected Condition: Distance has been adjusted from {0} to {1}, currentVelocity: {2} acceleration: {3}, targetVelocity: {4}",
				retVal.SimulationDistance, ds, currentSpeed, CurrentState.Acceleration, targetVelocity);
			throw new VectoSimulationException("Simulation distance unexpectedly adjusted! {0} -> {1}", ds, 
				retVal.SimulationDistance);
		}

		/// <summary>
		/// computes the distance required to decelerate from the current velocity to the given target velocity considering
		/// the drivers acceleration/deceleration curve.
		/// </summary>
		/// <param name="targetSpeed"></param>
		/// <returns></returns>
		public Meter ComputeDecelerationDistance(MeterPerSecond targetSpeed) => 
			DriverData.AccelerationCurve.ComputeDecelerationDistance(DataBus.VehicleInfo.VehicleSpeed, targetSpeed);

		/// <summary>
		/// Computes the time interval for driving the given distance ds with the vehicle's current speed and the given acceleration.
		/// If the distance ds can not be reached (i.e., the vehicle would halt before ds is reached) then the distance parameter is adjusted.
		/// Returns a new operating point (a, ds, dt)
		/// </summary>
		/// <param name="acceleration"></param>
		/// <param name="ds"></param>
		/// <returns>Operating point (a, ds, dt)</returns>
		private OperatingPoint ComputeTimeInterval(MeterPerSquareSecond acceleration, Meter ds) => 
			VectoMath.ComputeTimeInterval(DataBus.VehicleInfo.VehicleSpeed, acceleration, DataBus.MileageCounter.Distance, ds);

		/// <summary>
		/// simulate a certain time interval where the vehicle is stopped.
		/// </summary>
		/// <param name="absTime"></param>
		/// <param name="dt"></param>
		/// <param name="targetVelocity"></param>
		/// <param name="gradient"></param>
		/// <returns></returns>
		public IResponse DrivingActionHalt(Second absTime, Second dt, MeterPerSecond targetVelocity, Radian gradient)
		{
			DrivingAction = DrivingAction.Halt;
			if (!targetVelocity.IsEqual(0) || !DataBus.VehicleInfo.VehicleStopped) {
				Log.Error("TargetVelocity ({0}) and VehicleVelocity ({1}) must be zero when vehicle is halting!",
					targetVelocity,
					DataBus.VehicleInfo.VehicleSpeed);
				throw new VectoSimulationException(
					"TargetVelocity ({0}) and VehicleVelocity ({1}) must be zero when vehicle is halting!",
					targetVelocity,
					DataBus.VehicleInfo.VehicleSpeed);
			}

			DriverAcceleration = 0.SI<MeterPerSquareSecond>();
			var retVal = NextComponent.Request(absTime, dt, 0.SI<MeterPerSquareSecond>(), gradient, false);

			if (retVal is ResponseGearShift) {
				DriverAcceleration = 0.SI<MeterPerSquareSecond>();
				retVal = NextComponent.Request(absTime, dt, 0.SI<MeterPerSquareSecond>(), gradient, false);
			}
			CurrentState.dt = dt;
			CurrentState.Acceleration = 0.SI<MeterPerSquareSecond>();
			return retVal;
		}

		protected override void DoWriteModalResults(Second time, Second simulationInterval, IModalDataContainer container)
		{
			container[ModalResultField.acc] = CurrentState.Acceleration;
			container.SetDataValue("DriverAction", (int)DrivingAction);
			DriverStrategy.WriteModalResults(container);
		}


		protected override void DoCommitSimulationStep(Second time, Second simulationInterval)
		{
			if (CurrentState.Response != null && !(CurrentState.Response is ResponseSuccess)) {
				throw new VectoSimulationException("Previous request did not succeed!");
			}
			CurrentState.Response = null;
			DriverStrategy.CommitSimulationStep();
			if (_previousGearboxDisengaged.HasValue) {
				DataBus.GearboxCtl().DisengageGearbox = _previousGearboxDisengaged.Value;
				_previousGearboxDisengaged = null;
			}
		}

		public class DriverState
		{
			public Second dt;
			public MeterPerSquareSecond Acceleration;
			public IResponse Response;
		}

		[Flags]
		protected enum LimitationMode
		{
			NoLimitation = 0x0,
			LimitDecelerationDriver = 0x2,
			//LimitDecelerationLookahead = 0x4
		}

		public DrivingBehavior DriverBehavior { get; set; }

		public MeterPerSquareSecond DriverAcceleration { get; protected set; }

		public PCCStates PCCState => DriverStrategy.PCCState;

		public MeterPerSecond NextBrakeTriggerSpeed => DriverStrategy.BrakeTrigger?.NextTargetSpeed;
		public MeterPerSecond ApplyOverspeed(MeterPerSecond targetSpeed) => DriverStrategy.ApplyOverspeed(targetSpeed);

		protected override bool DoUpdateFrom(object other) => false;
	}
}