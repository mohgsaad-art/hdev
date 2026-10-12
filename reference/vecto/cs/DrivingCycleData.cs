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
using System.ComponentModel.DataAnnotations;
using System.Diagnostics;
using System.Linq;
using Newtonsoft.Json;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;

namespace TUGraz.VectoCore.Models.SimulationComponent.Data
{
	public enum CycleType
	{
		EngineOnly,
		DistanceBased,
		PWheel,
		MeasuredSpeed,
		MeasuredSpeedGear,
		PTO,
		EPTO,
		VTP,
		None,
		PTODuringDrive
	}

	public static class CycleTypeHelper
	{
		public static bool IsDistanceBased(this CycleType type)
		{
			return type == CycleType.DistanceBased;
		}
	}

	public interface IDrivingCycleData
	{
		List<DrivingCycleData.DrivingCycleEntry> Entries { get; }

		string Name { get; }
		
		CycleType CycleType { get; }
		
		void Finish();
	}

	[CustomValidation(typeof(DrivingCycleData), "ValidateCycleData")]
	public class DrivingCycleData : SimulationComponentData, IDrivingCycleData
	{
		internal DrivingCycleData() {}

		[JsonIgnore]
		public List<DrivingCycleEntry> Entries { get; internal set; }

		public string Name { get; internal set; }

		public CycleType CycleType { get; internal set; }

		public void Finish() {}

		// ReSharper disable once UnusedMember.Global -- used by Validation
		public static ValidationResult ValidateCycleData(DrivingCycleData cycleData, ValidationContext validationContext)
		{
			var mode = GetExecutionMode(validationContext);
			if (mode == ExecutionMode.Declaration) {
				return ValidationResult.Success;
			}

			var result = new List<string>();
			if (cycleData.CycleType.IsDistanceBased()) {
				var cur = cycleData.Entries[0].Distance;
				for (var i = 1; i < cycleData.Entries.Count; i++) {
					if (cycleData.Entries[i].Distance < cur) {
						result.Add(
							string.Format("distance-based cycle is not increasing strictly monotonous. entry: {0}, s_{1}: {2} s_{0}: {3}", i,
								i - 1, cycleData.Entries[i - 1].Distance, cycleData.Entries[i].Distance));
					}
					cur = cycleData.Entries[i].Distance;
				}
			} else {
				var cur = cycleData.Entries[0].Time;
				for (var i = 1; i < cycleData.Entries.Count; i++) {
					if (cycleData.Entries[i].Time < cur) {
						result.Add(
							string.Format("time-based cycle is not increasing strictly monotonous. entry: {0}, t_{1}: {2} t_{0}: {3}", i,
								i - 1, cycleData.Entries[i - 1].Time, cycleData.Entries[i].Time));
					}
					cur = cycleData.Entries[i].Time;
				}
			}
			if (result.Any()) {
				return new ValidationResult($"Validation of Cycle {cycleData.Name} failed", result);
			}
			return ValidationResult.Success;
		}

		[DebuggerDisplay(
			"s:{Distance}, t:{Time}, v:{VehicleTargetSpeed}, grad:{RoadGradient}, n:{AngularVelocity}, gear:{Gear}")]
		public class DrivingCycleEntry
		{
			public DrivingCycleEntry() {}

			public DrivingCycleEntry(DrivingCycleEntry entry)
			{
				Distance = entry.Distance;
				Time = entry.Time;
				VehicleTargetSpeed = entry.VehicleTargetSpeed;
				RoadGradient = entry.RoadGradient;
				Altitude = entry.Altitude;
				StoppingTime = entry.StoppingTime;
				AngularVelocity = entry.AngularVelocity;
				Gear = entry.Gear;
				AdditionalAuxPowerDemand = entry.AdditionalAuxPowerDemand;
				AirSpeedRelativeToVehicle = entry.AirSpeedRelativeToVehicle;
				WindYawAngle = entry.WindYawAngle;
				Torque = entry.Torque;
				Drag = entry.Drag;
				PTOActive = entry.PTOActive;
				AuxiliarySupplyPower = new Dictionary<string, Watt>(entry.AuxiliarySupplyPower);
				EngineSpeed = entry.EngineSpeed;
				FanSpeed = entry.FanSpeed;
				PTOPowerDemandDuringDrive = entry.PTOPowerDemandDuringDrive;
				PTOElectricalPowerDemand = entry.PTOElectricalPowerDemand;
				Highway = entry.Highway;
                PowerAdditonalHighVoltage = entry.PowerAdditonalHighVoltage;
				FanElectricalPower = entry.FanElectricalPower;
				CombustionEngineTorque = entry.CombustionEngineTorque;
				CH4MassFlow = entry.CH4MassFlow;
				COMassFlow = entry.COMassFlow;
				NMHCMassFlow = entry.NMHCMassFlow;
				NOxMassFlow = entry.NOxMassFlow;
				THCMassFlow = entry.THCMassFlow;
				PMNumberFlow = entry.PMNumberFlow;
				CO2MassFlow = entry.CO2MassFlow;
				OBFCMMileage = entry.OBFCMMileage;
				OBFCMFuelConsumptionMassFlow = entry.OBFCMFuelConsumptionMassFlow;
				OBFCMFuelConsumptionVolumeFlow = entry.OBFCMFuelConsumptionVolumeFlow;
				OBFCMMass = entry.OBFCMMass;
			}

			/// <summary>
			/// Travelled distance used for distance-based cycles. If "t" is also defined this column will be ignored.
			/// </summary>
			public Meter Distance;

			/// <summary>
			/// Used for time-based cycles. If neither this nor the distance. "s" is defined the data will be interpreted as 1Hz.
			/// </summary>
			public Second Time;

			/// <summary>
			/// Required except for Engine Only Mode calculations.
			/// </summary>
			public MeterPerSecond VehicleTargetSpeed;

			/// <summary>
			/// Optional.
			/// </summary>
			public Radian RoadGradient;

			/// <summary>
			/// [%] Optional.
			/// </summary>
			public Scalar RoadGradientPercent => (Math.Tan(RoadGradient.Value()) * 100).SI<Scalar>();

			public Dictionary<FuelType, KilogramPerSecond> Fuelconsumption;

			/// <summary>
			/// relative altitude of the driving cycle over distance
			/// </summary>
			public Meter Altitude;

			/// <summary>
			/// this section of the cycle is considered to be highway driving (used for PCC atm)
			/// </summary>
			public bool Highway;

			/// <summary>
			/// Required for distance-based cycles. Not used in time based cycles. "stop" defines the time the vehicle spends in stop phases.
			/// </summary>
			public Second StoppingTime;

			/// <summary>
			/// Supply Power input for each auxiliary defined in the .vecto file where xxx matches the ID of the corresponding
			/// Auxiliary. ID's are not case sensitive and must not contain space or special characters.
			/// </summary>
			public Dictionary<string, Watt> AuxiliarySupplyPower;

			/// <summary>
			/// If "n_eng_avg" is defined VECTO uses that instead of the calculated engine speed value.
			/// </summary>
			public PerSecond AngularVelocity;

			/// <summary>
			/// [-] Gear input. Overwrites the gear shift model.
			/// </summary>
			public uint Gear;

			/// <summary>
			/// This power input will be directly added to the engine power in addition to possible other auxiliaries. Also used in Engine Only Mode.
			/// </summary>
			public Watt AdditionalAuxPowerDemand;

			/// <summary>
			/// Only required if Cross Wind Correction is set to Vair and Beta Input.
			/// </summary>
			public MeterPerSecond AirSpeedRelativeToVehicle;

			/// <summary>
			/// [°] Only required if Cross Wind Correction is set to Vair and Beta Input.
			/// </summary>
			public double WindYawAngle;

			/// <summary>
			/// Effective engine torque at clutch. Only required in Engine Only Mode. Alternatively power "Pe" can be defined. Use "DRAG" to define motoring operation.
			/// </summary>
			public NewtonMeter Torque;

			public bool Drag;

			/// <summary>
			/// Power on the Wheels (only used in PWheel Mode).
			/// </summary>
			public Watt PWheel;

			public bool? TorqueConverterActive;

			/// <summary>
			/// The angular velocity at the wheel. only used in PWheelCycle.
			/// </summary>
			public PerSecond WheelAngularVelocity;

			/// <summary>
			/// Flag if PTO Cycle is active or not.
			/// </summary>
			public PTOActivity PTOActive;

			public PerSecond EngineSpeed;

			public PerSecond FanSpeed;

			public Watt FanElectricalPower;

			public NewtonMeter CombustionEngineTorque;

			public KilogramPerSecond CH4MassFlow;

			public KilogramPerSecond COMassFlow;

			public KilogramPerSecond NMHCMassFlow;

			public KilogramPerSecond NOxMassFlow;

			public KilogramPerSecond THCMassFlow;

			public KilogramPerSecond CO2MassFlow;

			public PerSecond PMNumberFlow;

			// required for VTP Mode (validation of cycle data in declaration mode)
			public NewtonMeter TorqueWheelLeft;

			public NewtonMeter TorqueWheelRight;

			public PerSecond WheelSpeedLeft;

			public PerSecond WheelSpeedRight;

			public bool VTPPSCompressorActive;

			public Meter OBFCMMileage;
			
			public Dictionary<FuelType, KilogramPerSecond> OBFCMFuelConsumptionMassFlow;
			
			public Dictionary<FuelType, LiterPerSecond> OBFCMFuelConsumptionVolumeFlow;
			
			public Kilogram OBFCMMass;

			// road sweeper application
			public Watt PTOPowerDemandDuringDrive;

			// Electrical pto cycle
			public Watt PTOElectricalPowerDemand;

			/// <summary>
			/// Additional high voltage power for PEVs.
			/// </summary>
            public Watt PowerAdditonalHighVoltage;
        }
	}

	public enum PTOActivity
	{
		Inactive = 0,
		PTOActivityDuringStop = 1,
		PTOActivityRoadSweeping = 2,
		PTOActivityWhileDrive = 3,
	}
}