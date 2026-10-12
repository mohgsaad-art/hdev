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
using System.Xml.Linq;
using Newtonsoft.Json;
using TUGraz.VectoCommon.BusAuxiliaries;
using TUGraz.VectoCommon.InputData;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Configuration;
using TUGraz.VectoCore.InputData.Reader.DataObjectAdapter.SimulationComponents;
using TUGraz.VectoCore.InputData.Reader.Impl;
using TUGraz.VectoCore.Models.Declaration;
using TUGraz.VectoCore.Models.Declaration.IterativeRunStrategies;
using TUGraz.VectoCore.Models.Declaration.PostMortemAnalysisStrategy;
using TUGraz.VectoCore.Models.Simulation.DataBus;
using TUGraz.VectoCore.Models.SimulationComponent.Data;
using TUGraz.VectoCore.Models.SimulationComponent.Data.ElectricComponents;
using TUGraz.VectoCore.Models.SimulationComponent.Data.ElectricComponents.Battery;
using TUGraz.VectoCore.Models.SimulationComponent.Data.Gearbox;
using TUGraz.VectoCore.Models.SimulationComponent.Strategies;
using TUGraz.VectoCore.OutputData;
using DriverData = TUGraz.VectoCore.Models.SimulationComponent.Data.DriverData;

namespace TUGraz.VectoCore.Models.Simulation.Data
{


	[CustomValidation(typeof(VectoRunData), "ValidateRunData")]
	public class VectoRunData : SimulationComponentData
	{
		public VectoRunData()
		{
			Exempted = false;
			JobType = VectoSimulationJobType.ConventionalVehicle;
			DCDCData = new DCDCData() {
				DCDCEfficiency = DeclarationData.DCDCEfficiency,
			};
		}

		public VectoSimulationJobType JobType { get; internal set; }
		public MeterPerSecond VehicleDesignSpeed { get; internal set; }

		[ValidateObject]
		public VehicleData VehicleData { get; internal set; }

		[ValidateObject]
		public AirdragData AirdragData { get; internal set; }

		[ValidateObject]
		public CombustionEngineData EngineData { get; internal set; }

		[ValidateObject]
		public GearboxData GearboxSinglePwt { get; internal set; }

		[ValidateObject]
		public AxleGearData AxleGearSinglePwt { get; internal set; }

		[ValidateObject]
		public AngledriveData AngledriveSinglePwt { get; internal set; }

		[ValidateObject]
		public IList<AxlePowertrainData> AxlePowertrains { get; internal set; } = new List<AxlePowertrainData>();

        [Required, ValidateObject]
		[JsonIgnore]
		public IDrivingCycleData Cycle { get; internal set; }

		[ValidateObject]
		public IEnumerable<AuxData> Aux { get; internal set; }

		public IAuxiliaryConfig BusAuxiliaries { get; internal set; }

		[ValidateObject]
		public RetarderData RetarderSinglePwt { get; internal set; }

		[ValidateObject]
		public PTOData PTOSinglePwt { get; internal set; }

		[ValidateObject]
		public DriverData DriverData { get; internal set; }

		public ExecutionMode ExecutionMode { get; internal set; }

		[Required, MinLength(1)]
		public string JobName { get; internal set; }

		public string ModFileSuffix { get; internal set; }

		[ValidateObject]
		[JsonIgnore]
		public IDeclarationReport Report { get; internal set; }

		[Required, ValidateObject]
		public LoadingType Loading { get; internal set; }

		[ValidateObject]
		[JsonIgnore]
		public Mission Mission { get; internal set; }

		[JsonIgnore]
		public XElement InputDataHash { get; internal set; }

		public int JobRunId { get; internal set; }

		public AuxFanData FanDataVTP { get; internal set; }

		public IList<Tuple<PowertrainPosition, ElectricMotorData>> ElectricMachinesSinglePwt { get; internal set; }

		public BatterySystemData BatteryData { get; internal set; }

		public SuperCapData SuperCapData { get; internal set; }

		public FuelCellSystemData FuelCellSystemData { get; internal set; }

		public DCDCData DCDCData { get; internal set; }

		public SimulationType SimulationType { get; internal set; }

		public VTPData VTPData { get; internal set; }

		public ShiftStrategyParameters GearshiftParametersSinglePwt { get; internal set; }

		public bool Exempted { get; internal set; }

		public bool MultistageRun { get; internal set; }

		public IDrivingCycleData PTOCycleWhileDrive { get; internal set; }

		public string GetShiftStrategy(int axleNumber = Constants.NOT_IN_AXLE_POWERTRAIN)
		{
			var gearboxKVP = GetGearboxData().FirstOrDefault(x => x.Item1 == axleNumber);
			return (gearboxKVP == default) ? null : gearboxKVP.Item2.ShiftStrategy;
		}

		// only used for factor method
		public IResult PrimaryResult { get; set; }

		public HybridStrategyParameters HybridStrategyParameters { get; internal set; }

		public Watt ElectricAuxDemand { get; internal set; }

		[JsonIgnore]
		public IMultistageVIFInputData MultistageVifInputData { get; internal set; }

		// container to pass genset data from powertrain to post-processing, not filled by dataadapter/rundatafactory
		public GenSetData GenSet { get; set; }
		[JsonIgnore]
		public IDeclarationInputDataProvider InputData { get; internal set; }

		// used to identify job and run in summary container
		public int JobNumber { get; set; }
		public int RunNumber { get; set; }
		public int Iteration { get; set; }


		public OvcHevMode OVCMode { get; internal set; }

		public bool BatteryOnlyHybridMode { get; internal set; }

		public Watt MaxChargingPower { get; internal set; }

		public bool InMotionCharging { get; internal set; }

		public IMCTechnology InMotionChargingTechnology { get; internal set; }

        [JsonIgnore]
		public IIterativeRunStrategy IterativeRunStrategy { get; internal set; } = new DefaultIterativeStrategy();

		[JsonIgnore]
		public IPostMortemAnalyzeStrategy PostMortemStrategy { get; internal set; } = new DefaultPostMortemAnalyzeStrategy();
		
		public NewtonMeter TorqueDriftLeftWheel { get; internal set; }

		public NewtonMeter TorqueDriftRightWheel { get; internal set; }

		public WheelEndData WheelEndData { get; internal set; }

		[DebuggerDisplay("{ID}: {PowerDemandMech}/{PowerDemandElectric}")]
		public class AuxData
        {
            // ReSharper disable once InconsistentNaming
            public string ID;

			public IList<string> Technology;

			[SIRange(0, 100 * Constants.Kilo)]
			public Watt PowerDemandMech;

			[SIRange(0, 100 * Constants.Kilo)]
			public Watt PowerDemandElectric;

            public delegate Watt PowerDemandFunc(IDataBus dataBus, bool mechPower = true);

            [JsonIgnore]
			public Func<DrivingCycleData.DrivingCycleEntry, Watt> PowerDemandMechCycleFunc;

			[JsonIgnore]
			public PowerDemandFunc PowerDemandDataBusFunc;

			[Required]
			public AuxiliaryDemandType DemandType;

			[Required]
			public bool ConnectToREESS;

			[Required]
			public bool IsFullyElectric;

			public MissionType? MissionType;
		}

		// container to pass genset data from powertrain to post-processing, not filled by dataadapter/rundatafactory
		public class GenSetData
		{
			public GenSetCharacteristics GenSetCharacteristics { get; set; }
		}

		public static ValidationResult ValidateRunData(VectoRunData runData, ValidationContext validationContext)
		{
			var gearboxData = runData.GearboxSinglePwt;
			var engineData = runData.EngineData;

			var jobType = GetSimulationJobType(validationContext);

			if (jobType == VectoSimulationJobType.ConventionalVehicle || jobType == VectoSimulationJobType.ParallelHybridVehicle) {
				if (runData.AxleGearSinglePwt == null) {
					return new ValidationResult("Axlegear data is required for conventional and parallel hybrid vehicles!");
				}
				
				if (gearboxData == null) {
					return new ValidationResult("Gearbox data is required for conventional and parallel hybrid vehicles!");
				}

				if (engineData == null) {
					return new ValidationResult("Combustion engine data is required for conventional and parallel hybrid vehicles!");
				}

				var validationResult = CheckPowertrainLossMapsSizeConventionalPT(runData, gearboxData, engineData);
				if (validationResult != null) {
					return validationResult;
				}
			}

			if (runData.Cycle != null && runData.Cycle.Entries.Any(e => e.PTOActive == PTOActivity.PTOActivityDuringStop)) {

				if (runData.PTOSinglePwt == null || runData.PTOSinglePwt.PTOCycle == null) {
					return new ValidationResult("PTOCycle is used in DrivingCycle, but is not defined in Vehicle-Data.");
				}
			}

			if (runData.Cycle != null && runData.Cycle.Entries.Any(x => x.PTOActive == PTOActivity.PTOActivityRoadSweeping)) {
				if (runData.EngineData.PTORoadSweepEngineSpeed == null) {
					return new ValidationResult("RoadSweeping PTO activity detected in cycle but no min. engine speed during road sweeping provided");
				}

				if (runData.DriverData.PTODriveRoadsweepingGear == null || runData.DriverData.PTODriveRoadsweepingGear.Equals(new GearshiftPosition(0))) {
					return new ValidationResult("RoadSweeping PTO activity detected in cycle but no gear during road sweeping provided");
				}
			}

			if (runData.Cycle != null && runData.Cycle.Entries.Any(x => x.PTOActive == PTOActivity.PTOActivityWhileDrive)) {
				if (runData.PTOCycleWhileDrive == null || runData.PTOCycleWhileDrive.Entries.Count == 0) {
					return new ValidationResult("PTO activity while driving detected in cycle but PTO cycle provided");
				}
			}

			if ((jobType == VectoSimulationJobType.ConventionalVehicle || jobType == VectoSimulationJobType.ParallelHybridVehicle) && runData.EngineData.PTORoadSweepEngineSpeed != null) {
				if (runData.EngineData.IdleSpeed.IsGreater(runData.EngineData.PTORoadSweepEngineSpeed)) {
					return new ValidationResult("PTO Operating enginespeed is below engine idling speed");
				}

				if (runData.EngineData.FullLoadCurves[0].N95hSpeed.IsSmaller(runData.EngineData.PTORoadSweepEngineSpeed)) {
					return new ValidationResult("PTO operating enginespeed is above n_95h");
				}
			}

			if (runData.ElectricMachinesSinglePwt?.Any(e => e.Item1 == PowertrainPosition.HybridP0) ?? false){
				return new ValidationResult("P0 Hybrids are modeled as SmartAlternator in the BusAuxiliary model.");
			}

			return ValidationResult.Success;
		}

		public List<Tuple<EMPlacement, ElectricMotorData>> GetEMData()
		{
			var nonAxleEMS = ElectricMachinesSinglePwt?
				.Select(x => new Tuple<EMPlacement, ElectricMotorData>(
					new EMPlacement(x.Item1, Constants.NOT_IN_AXLE_POWERTRAIN), x.Item2)).ToList()
				?? new List<Tuple<EMPlacement, ElectricMotorData>>();

			var axleEMs = AxlePowertrains
				.Where(x => x.ElectricMachineData != null)
				.Select(x => new Tuple<EMPlacement, ElectricMotorData>(
						new EMPlacement(x.ElectricMachineData.Item1, x.AxleNumber), x.ElectricMachineData.Item2)).ToList();

			return nonAxleEMS.Concat(axleEMs).ToList();
		}

		public List<Tuple<int, ShiftStrategyParameters>> GetGearshiftParameters()
		{
			var shiftParams = new List<Tuple<int, ShiftStrategyParameters>>();
			
			if (GearshiftParametersSinglePwt != null)
			{
				shiftParams.Add(new Tuple<int, ShiftStrategyParameters>(Constants.NOT_IN_AXLE_POWERTRAIN, GearshiftParametersSinglePwt));
			}

			var shiftParamsInAxlePt = AxlePowertrains
				.Where(x => x.GearshiftParameters != null)
				.Select(x => new Tuple<int, ShiftStrategyParameters>(x.AxleNumber, x.GearshiftParameters));

			return shiftParams.Concat(shiftParamsInAxlePt).ToList();
		}

		public List<Tuple<int, GearboxData>> GetGearboxData()
		{
			var gearboxes = new List<Tuple<int, GearboxData>>();

			if (GearboxSinglePwt != null)
			{
				gearboxes.Add(new Tuple<int, GearboxData>(Constants.NOT_IN_AXLE_POWERTRAIN, GearboxSinglePwt));
			}

			var gearboxesInAxlePt = AxlePowertrains
				.Where(x => x.GearboxData != null)
				.Select(x => new Tuple<int, GearboxData>(x.AxleNumber, x.GearboxData));

			return gearboxes.Concat(gearboxesInAxlePt).ToList();
		}

		public List<Tuple<int, AxleGearData>> GetAxlegearData()
		{
			var axlegearData = new List<Tuple<int, AxleGearData>>();

			if (AxleGearSinglePwt != null)
			{
				axlegearData.Add(new Tuple<int, AxleGearData>(Constants.NOT_IN_AXLE_POWERTRAIN, AxleGearSinglePwt));
			}

			var axlegearInAxlePt = AxlePowertrains
				.Where(x => x.AxleGearData != null)
				.Select(x => new Tuple<int, AxleGearData>(x.AxleNumber, x.AxleGearData));

			return axlegearData.Concat(axlegearInAxlePt).ToList(); 
		}

		public List<Tuple<int, AngledriveData>> GetAngledriveData()
		{
			var angledriveData = new List<Tuple<int, AngledriveData>>();

			if (AngledriveSinglePwt != null)
			{
				angledriveData.Add(new Tuple<int, AngledriveData>(Constants.NOT_IN_AXLE_POWERTRAIN, AngledriveSinglePwt));
			}

			var angledriverInAxlePt = AxlePowertrains
				.Where(x => x.AngledriveData != null)
				.Select(x => new Tuple<int, AngledriveData>(x.AxleNumber, x.AngledriveData));

			return angledriveData.Concat(angledriverInAxlePt).ToList();
		}

		public List<Tuple<int, RetarderData>> GetRetarderData()
		{
			var retarderData = new List<Tuple<int, RetarderData>>();

			if (RetarderSinglePwt != null)
			{
				retarderData.Add(new Tuple<int, RetarderData>(Constants.NOT_IN_AXLE_POWERTRAIN, RetarderSinglePwt));
			}

			var retardersInAxlePt = AxlePowertrains
				.Where(x => x.Retarder != null)
				.Select(x => new Tuple<int, RetarderData>(x.AxleNumber, x.Retarder));

			return retarderData.Concat(retardersInAxlePt).ToList();
		}

		public List<Tuple<int, PTOData>> GetPTOData()
		{
			var ptoData = new List<Tuple<int, PTOData>>();

			if (PTOSinglePwt != null)
			{
				ptoData.Add(new Tuple<int, PTOData>(Constants.NOT_IN_AXLE_POWERTRAIN, PTOSinglePwt));
			}

			var ptosInAxlePt = AxlePowertrains
				.Where(x => x.PTO != null)
				.Select(x => new Tuple<int, PTOData>(x.AxleNumber, x.PTO));

            return ptoData.Concat(ptosInAxlePt).ToList();
		}

		private static ValidationResult CheckPowertrainLossMapsSizeConventionalPT(VectoRunData runData, GearboxData gearboxData, 
			CombustionEngineData engineData)
		{
			
			var axleGearData = runData.AxleGearSinglePwt;
			var angledriveData = runData.AngledriveSinglePwt;
			var hasAngleDrive = angledriveData != null && angledriveData.Angledrive != null;
			var angledriveRatio = hasAngleDrive && angledriveData.Type == AngledriveType.SeparateAngledrive
				? angledriveData.Angledrive.Ratio
				: 1.0;
			var axlegearRatio = axleGearData?.AxleGear.Ratio ?? 1.0;
			var dynamicTyreRadius = runData.VehicleData != null ? runData.VehicleData.DynamicTyreRadius : 0.0.SI<Meter>();

			var vehicleMaxSpeed = runData.EngineData.FullLoadCurves[0].N95hSpeed /
								runData.GearboxSinglePwt.Gears[runData.GearboxSinglePwt.Gears.Keys.Max()].Ratio / axlegearRatio /
								angledriveRatio * dynamicTyreRadius;
			var maxSpeed = VectoMath.Min(vehicleMaxSpeed, (runData.VehicleDesignSpeed ?? 90.KMPHtoMeterPerSecond()) + (runData.DriverData?.OverSpeed?.OverSpeed ?? 0.KMPHtoMeterPerSecond()));

			var gearsInput = GearboxDataAdapterBase.FilterDisabledGears(runData.VehicleData.InputData.TorqueLimits, gearboxData.InputData);
			var gears = gearboxData.Gears.Where(f => gearsInput.Any(g => f.Key == g.Gear)).ToList();
			
			if (gears.Count + 1 != engineData.FullLoadCurves.Count) {
				return
					new ValidationResult(
						$"number of full-load curves in engine does not match gear count. " +
						$"engine fld: {engineData.FullLoadCurves.Count}, gears: {gears.Count}");
			}

			foreach (var gear in gears) {
				var maxEngineSpeed = VectoMath.Min(engineData.FullLoadCurves[gear.Key].RatedSpeed, gear.Value.MaxSpeed);
				for (var angularVelocity = engineData.IdleSpeed;
					angularVelocity < maxEngineSpeed;
					angularVelocity += 2.0 / 3.0 * (maxEngineSpeed - engineData.IdleSpeed) / 10.0) {
					if (!gear.Value.HasLockedGear) {
						continue;
					}

					var velocity = angularVelocity / gear.Value.Ratio / angledriveRatio / axlegearRatio * dynamicTyreRadius;

					if (velocity > maxSpeed) {
						continue;
					}

					for (var inTorque = engineData.FullLoadCurves[gear.Key].FullLoadStationaryTorque(angularVelocity) / 3;
						inTorque < engineData.FullLoadCurves[gear.Key].FullLoadStationaryTorque(angularVelocity);
						inTorque += 2.0 / 3.0 * engineData.FullLoadCurves[gear.Key].FullLoadStationaryTorque(angularVelocity) / 10.0) {
						var validateRunData = CheckLossMapsEntries(gear, angularVelocity, inTorque, angledriveData, axleGearData, velocity);
						if (validateRunData != null) {
							return validateRunData;
						}
					}
				}
			}
			return null;
		}

		private static ValidationResult CheckLossMapsEntries(KeyValuePair<uint, GearData> gear, PerSecond engineSpeed,
			NewtonMeter inTorque, AngledriveData angledriveData, AxleGearData axleGearData, MeterPerSecond velocity)
		{
			var hasAngleDrive = angledriveData != null && angledriveData.Angledrive != null;
			var angledriveRatio = hasAngleDrive && angledriveData.Type == AngledriveType.SeparateAngledrive
				? angledriveData.Angledrive.Ratio
				: 1.0;

			var tqLoss = gear.Value.LossMap.GetTorqueLoss(engineSpeed / gear.Value.Ratio, inTorque * gear.Value.Ratio);
			if (tqLoss.Extrapolated) {
				return new ValidationResult($"Interpolation of Gear-{gear.Key}-LossMap failed " +
											$"with torque={inTorque} " +
											$"and angularSpeed={engineSpeed.ConvertToRoundsPerMinute()}");

			}
			var angledriveTorque = (inTorque - tqLoss.Value) / gear.Value.Ratio;


			var axlegearTorque = angledriveTorque;
			if (hasAngleDrive) {
				var anglTqLoss = angledriveData.Angledrive.LossMap.GetTorqueLoss(
					engineSpeed / gear.Value.Ratio / angledriveRatio,
					angledriveTorque * angledriveRatio);
				if (anglTqLoss.Extrapolated) {
					return new ValidationResult("Interpolation of Angledrive-LossMap failed " +
												$"with torque={angledriveTorque} " +
												$"and angularSpeed={(engineSpeed / gear.Value.Ratio).ConvertToRoundsPerMinute()}");
				}
			}

			if (axleGearData != null) {
				var axleAngularVelocity = engineSpeed / gear.Value.Ratio / angledriveRatio / axleGearData.AxleGear.Ratio;
				
				var axlTqLoss = axleGearData.AxleGear.LossMap.GetTorqueLoss(axleAngularVelocity, axlegearTorque * axleGearData.AxleGear.Ratio);
				if (axlTqLoss.Extrapolated) { 
				return new ValidationResult("Interpolation of AxleGear-LossMap failed " +
											$"with torque={axlegearTorque} " +
											$"and angularSpeed={axleAngularVelocity.ConvertToRoundsPerMinute()} " +
											$"(gear={gear.Key}, velocity={velocity})");
				}
			}
			return null;
		}

	}

	public class VTPData
	{
		public Dictionary<FuelType, double> CorrectionFactors;

		public IList<IFuelNCVData> FuelNCVs;
	}

	public class AuxFanData
	{
		public double[] FanCoefficients;

		public Meter FanDiameter;
	}

}