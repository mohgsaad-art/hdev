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
using System.IO;
using System.Linq;
using TUGraz.VectoCommon.BusAuxiliaries;
using TUGraz.VectoCommon.Exceptions;
using TUGraz.VectoCommon.InputData;
using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Configuration;
using TUGraz.VectoCore.InputData.FileIO.JSON;
using TUGraz.VectoCore.InputData.Impl;
using TUGraz.VectoCore.InputData.Reader.ComponentData;
using TUGraz.VectoCore.InputData.Reader.DataObjectAdapter;
using TUGraz.VectoCore.Models.BusAuxiliaries.DownstreamModules.Impl.Electrics;
using TUGraz.VectoCore.Models.Declaration.Auxiliaries;
using TUGraz.VectoCore.Models.Declaration.VehicleOperation;
using TUGraz.VectoCore.Models.SimulationComponent.Data;
using TUGraz.VectoCore.Models.SimulationComponent.Data.ElectricMotor;
using TUGraz.VectoCore.Models.SimulationComponent.Data.Engine;
using TUGraz.VectoCore.Models.SimulationComponent.Data.Gearbox;
using TUGraz.VectoCore.Utils;
using TUGraz.VectoCore.Models.BusAuxiliaries.DownstreamModules.Impl.HVAC;
using TUGraz.VectoCore.Models.Simulation.Data;
using TUGraz.VectoCore.Models.Simulation.Impl;
using TUGraz.VectoCore.Models.SimulationComponent.Data.ElectricComponents.Battery;
using TUGraz.VectoCore.Models.SimulationComponent.Impl;
using TUGraz.VectoCore.OutputData;
using Point = TUGraz.VectoCommon.Utils.Point;
using TUGraz.VectoCore.InputData.Reader.DataObjectAdapter.SimulationComponents;
using ElectricSystem = TUGraz.VectoCore.Models.Declaration.Auxiliaries.ElectricSystem;

namespace TUGraz.VectoCore.Models.Declaration
{
	public static class 
		DeclarationData
	{
		/// <summary>
		/// The standard acceleration for gravity on earth.
		/// http://physics.nist.gov/Pubs/SP330/sp330.pdf (page 52)
		/// </summary>
		public static readonly MeterPerSquareSecond GravityAccelleration = 9.80665.SI<MeterPerSquareSecond>();

		public static readonly KilogramPerCubicMeter AirDensity = 1.188.SI<KilogramPerCubicMeter>();


		public const string DeclarationDataResourcePrefix = "TUGraz.VectoCore.Resources.Declaration";

		public static readonly Watt MinEnginePowerForEMS = 300e3.SI<Watt>();
		public static readonly Watt MinEnginePowerForEMS_PEV = 300e3.SI<Watt>();

		public static readonly TruckSegments TruckSegments = new TruckSegments();
		public static readonly PrimaryBusSegments PrimaryBusSegments = new PrimaryBusSegments();
		public static readonly CompletedBusSegments CompletedBusSegments = new CompletedBusSegments();
		public static readonly Wheels Wheels = new Wheels();
		public static readonly PT1 PT1 = new PT1();
		public static readonly FuelData FuelData = FuelData.Instance();
		public static readonly ElectricSystem ElectricSystem = new ElectricSystem();
		public static readonly Fan Fan = new Fan();

		public static readonly HeatingVentilationAirConditioning HeatingVentilationAirConditioning =
			new HeatingVentilationAirConditioning();


		public static readonly PneumaticSystem PneumaticSystem = new PneumaticSystem();
		public static readonly SteeringPump SteeringPump = new SteeringPump();
		public static readonly SteeringPumpBus SteeringPumpBus = new SteeringPumpBus();
		public static readonly WHTCCorrection WHTCCorrection = new WHTCCorrection();
		public static readonly AirDrag AirDrag = new AirDrag();

		public static readonly StandardBodies StandardBodies = new StandardBodies();
		public static readonly Conditioning Conditioning = new Conditioning();
		public static readonly Payloads Payloads = new Payloads();

		public static readonly PTOTransmission PTOTransmission = new PTOTransmission();

		public static readonly HEVStrategyParameters HEVStrategyParameters = new HEVStrategyParameters();

		public const double HEV_EquivalenceFactor_Min = 0.1;
		public const double HEV_EquivalenceFactor_Max = 4.0;
		//public static readonly HEVStrategyParameters InitEquivalenceFactorsBus = new HEVStrategyParametersBus();

		public static readonly VehicleOperationLookup VehicleOperation = new VehicleOperationLookup();

		public static readonly IMCTechnologyLookup ImcTechnology = new IMCTechnologyLookup();

		public static readonly double ElectricMachineDefaultMechanicalTransmissionEfficiency = 1;
		//public static MeterPerSecond CycleSpeedLimit;
		public const double LossMapExtrapolationFactor = 6;

		public static readonly ADASCombinations ADASCombinations = new ADASCombinations();

		public static readonly WeightingGroups WeightingGroup = new WeightingGroups();
		public static readonly WeightingFactors WeightingFactors = new WeightingFactors();

		public const double AlternatorEfficiency = 0.7;
		public const double DCDCEfficiency = 1.0;

		public const double HVACElectricEfficiencyFactor = 0.8;

		public const double WHRChargerEfficiency = 0.98;

		public const double OverloadRecoveryFactor = 0.9;

		public static readonly Ohm SuperCapMinInternalResistance = 5.SI(Unit.SI.Milli.Ohm).Cast<Ohm>();
		public static readonly Volt SuperCapReferenceVoltage = 2.7.SI<Volt>();
		public const double SuperCapInternalResistanceStdValuesCorrection = 0.25;

		public const double ElectricMachineDefaultEfficiencyFallback = 0.98;

		public static readonly Watt MinDepotChgPwr = 10.SI(Unit.SI.Kilo.Watt).Cast<Watt>();
		public static readonly Second DepotChargingDuration = 6.SI(Unit.SI.Hour).Cast<Second>();
		public static readonly KilogramPerCubicMeter ICE_MassPerDisplacement = 770.SI<Kilogram>() / 7.7.SI<Liter>().Cast<CubicMeter>();
		public static readonly KilogramPerWatt EM_MassPerPower = 1.3.SI(Unit.SI.Kilo.Gramm.Per.Kilo.Watt).Cast<KilogramPerWatt>();
		public static readonly Kilogram EM_MassElectronics = 0.SI<Kilogram>();
		public static readonly Kilogram EM_MassInverter = 100.SI<Kilogram>();
		public static readonly KilogramPerWattSecond Battery_MassPerCapacity = 6.7.SI(Unit.SI.Kilo.Gramm.Per.Kilo.Watt.Hour).Cast<KilogramPerWattSecond>();

		public static readonly WheelEndStdFrictions WwheelEndStdFrictions = new WheelEndStdFrictions();

		public static readonly KilogramPerWatt FuelCell_MassPerPower = (1 / 0.65).SI(Unit.SI.Kilo.Gramm.Per.Kilo.Watt).Cast<KilogramPerWatt>();

        /// <summary>
        /// Formula for calculating the payload for a given gross vehicle weight.
        /// (so called "pc-formula", Whitebook Apr 2016, Part 1, p.187)
        /// </summary>
        public static Kilogram GetPayloadForGrossVehicleWeight(Kilogram grossVehicleWeight, string equationName)
		{
			if (equationName.ToLowerInvariant().StartsWith("pc10")) {
				return Payloads.Lookup10Percent(grossVehicleWeight);
			}

			if (equationName.ToLowerInvariant().StartsWith("pc75")) {
				return Payloads.Lookup75Percent(grossVehicleWeight);
			}

			return Payloads.Lookup50Percent(grossVehicleWeight);
		}

		/// <summary>
		/// Returns the payload for a trailer. This is 75% of (GVW-CurbWeight).
		/// </summary>
		public static Kilogram GetPayloadForTrailerWeight(Kilogram grossVehicleWeight, Kilogram curbWeight,
			bool lowLoading)
		{
			return
				(Math.Round(
					(Payloads.LookupTrailer(grossVehicleWeight, curbWeight) / (lowLoading ? 7.5 : 1)).LimitTo(
						0.SI<Kilogram>(),
						grossVehicleWeight - curbWeight).Value() / 100, 0) * 100).SI<Kilogram>();
		}

		public static Tuple<VehicleClass, bool?> GetVehicleGroupGroup(IVehicleDeclarationInputData vehicleData)
		{
			switch (vehicleData.VehicleCategory) {
				case VehicleCategory.Van:
				case VehicleCategory.RigidTruck:
				case VehicleCategory.Tractor:
					try {
						var truckSegment = DeclarationData.TruckSegments.Lookup(
							vehicleData.VehicleCategory,
							vehicleData.AxleConfiguration,
							vehicleData.GrossVehicleMassRating,
							vehicleData.CurbMassChassis,
							vehicleData.VocationalVehicle);

						return Tuple.Create(truckSegment.VehicleClass, (bool?)vehicleData.VocationalVehicle);
					} catch (VectoException) {
						var truckSegment = DeclarationData.TruckSegments.Lookup(
							vehicleData.VehicleCategory,
							vehicleData.AxleConfiguration,
							vehicleData.GrossVehicleMassRating,
							vehicleData.CurbMassChassis,
							false);

						return Tuple.Create(truckSegment.VehicleClass, (bool?)false);
					}
				case VehicleCategory.HeavyBusPrimaryVehicle:
					var primarySegment = DeclarationData.PrimaryBusSegments.Lookup(
						vehicleData.VehicleCategory,
						vehicleData.AxleConfiguration, 
						vehicleData.Articulated);

					return Tuple.Create(primarySegment.VehicleClass, (bool?)null);
				case VehicleCategory.HeavyBusCompletedVehicle:
					var segment = DeclarationData.CompletedBusSegments.Lookup(
						vehicleData.AxleConfiguration.NumAxles(),
						vehicleData.VehicleCode,
						vehicleData.RegisteredClass,
						vehicleData.NumberPassengerSeatsLowerDeck, 
						vehicleData.Height,
						vehicleData.LowEntry);

					return Tuple.Create(segment.VehicleClass, (bool?)null);
			}

			throw new VectoException("No Group found for vehicle");
		}


		public static SegmentLookup GetTruckSegment(IVehicleDeclarationInputData vehicle, bool batteryElectric = false, bool throwException = true)
		{
			var allowVocational = true;
			var ng = vehicle.ExemptedVehicle ? false : vehicle.Components.EngineInputData?.EngineModes.Any(e =>
				e.Fuels.Any(f => f.FuelType.IsOneOf(FuelType.LPGPI, FuelType.NGCI, FuelType.NGPI))) ?? false;
			var ovcHev = vehicle.ExemptedVehicle ? false : vehicle.OVC;
			Segment segment = new Segment();
			try {
				segment = DeclarationData.TruckSegments.Lookup(
					vehicle.VehicleCategory, batteryElectric, vehicle.AxleConfiguration, vehicle.GrossVehicleMassRating,
					vehicle.CurbMassChassis,
					vehicle.VocationalVehicle, ng, ovcHev);
			} catch (VectoException) {
				allowVocational = false;
				try
				{
					segment = DeclarationData.TruckSegments.Lookup(
					vehicle.VehicleCategory, batteryElectric, vehicle.AxleConfiguration, vehicle.GrossVehicleMassRating,
					vehicle.CurbMassChassis,
					false, ng, ovcHev);
				}
				catch (VectoException) { }
			}

			if (!segment.Found && allowVocational)
			{
                allowVocational = false;
                segment = DeclarationData.TruckSegments.Lookup(
                    vehicle.VehicleCategory, batteryElectric, vehicle.AxleConfiguration, vehicle.GrossVehicleMassRating,
                    vehicle.CurbMassChassis,
                    false, ng, ovcHev);
            }

			if (!segment.Found && throwException) {
				throw new VectoException(
					"no segment found for vehicle configuration: vehicle category: {0}, axle configuration: {1}, GVMR: {2}",
					vehicle.VehicleCategory, vehicle.AxleConfiguration,
					vehicle.GrossVehicleMassRating);
			}

			return new SegmentLookup() { Segment = segment, AllowVocational = allowVocational };
		}


		public struct SegmentLookup
		{
			public Segment Segment { get; set; }

			public bool AllowVocational { get; set; }
		}

		/// <summary>
		/// Checks whether the LH subgroup conditions are met, otherwise RD allocation needs to be carried out.
		/// </summary>
		/// <param name="result">Simulation cycle result entry.</param>
		/// <returns>True if RD allocation is needed; false otherwise.</returns>
		public static bool EvaluateLHSubgroupConditions(IResultEntry result)
		{
			Meter electricOprerationalRange = result.VectoRunData?.JobType.IsBatteryElectric() ?? false ?
				(result.ActualChargeDepletingRange ?? 0.SI<Meter>()) :
				double.MaxValue.SI<Meter>();

			return result.Mission == MissionType.LongHaul &&
				result.LoadingType == LoadingType.ReferenceLoad &&
				electricOprerationalRange < 350000.SI<Meter>();
		}

		public static WeightingGroup GetVehicleGroupCO2StandardsGroup(IVehicleDeclarationInputData vehicleData, double? electricRange, VehicleClass actualVehicleClass = VehicleClass.Unknown)
		{
			switch (vehicleData.VehicleCategory) {
				case VehicleCategory.Van:
				case VehicleCategory.RigidTruck:
				case VehicleCategory.Tractor:
					var vehicleGroup = GetVehicleGroupGroup(vehicleData);
					var co2Group = WeightingGroup.Lookup(
						vehicleGroup.Item1,
						vehicleData.SleeperCab ?? false,
						GetReferencePropulsionPower(vehicleData),
						vehicleData.VehicleType.IsBatteryElectric(),
						electricRange);
					return co2Group;
				case VehicleCategory.HeavyBusCompletedVehicle:
				case VehicleCategory.HeavyBusPrimaryVehicle:
					return WeightingGroup.Lookup(
						actualVehicleClass,
						false,
						GetReferencePropulsionPower(vehicleData),
						vehicleData.VehicleType.IsBatteryElectric(),
						electricRange);
				default:
					return Declaration.WeightingGroup.Unknown;
			}
		}

		public static WeightingGroup GetVehicleGroupCO2StandardsGroup(IMultistepBusInputDataProvider multiStageInputDataProvider)
		{
			var vehicleData = multiStageInputDataProvider.JobInputData.PrimaryVehicle.Vehicle;
			switch (vehicleData.VehicleCategory)
			{
				case VehicleCategory.HeavyBusCompletedVehicle:
					return WeightingGroup.Lookup(
						GetVehicleGroupGroup(vehicleData).Item1,
						false,
						GetReferencePropulsionPower(vehicleData),
						vehicleData.VehicleType.IsBatteryElectric(),
						null);
				case VehicleCategory.HeavyBusPrimaryVehicle:
					var completedVehicleData = multiStageInputDataProvider.JobInputData.ConsolidateManufacturingStage.Vehicle;
					return WeightingGroup.Lookup(
						GetVehicleGroupGroup(completedVehicleData).Item1,
						false,
						GetReferencePropulsionPower(vehicleData),
						vehicleData.VehicleType.IsBatteryElectric(),
						null);
				default:
					return Declaration.WeightingGroup.Unknown;
			}
		}

		public static Watt GetReferencePropulsionPower(IVehicleDeclarationInputData vehicleData)
		{
			switch (vehicleData.VehicleType) {
				case VectoSimulationJobType.ConventionalVehicle:
				case VectoSimulationJobType.ParallelHybridVehicle:
				case VectoSimulationJobType.EngineOnlySimulation:
				case VectoSimulationJobType.IHPC:
					return (vehicleData.Components?.EngineInputData?.RatedPowerDeclared ?? 0.SI<Watt>()) + (vehicleData.MaxNetPower1 ?? 0.SI<Watt>());
				case VectoSimulationJobType.SerialHybridVehicle:
				case VectoSimulationJobType.BatteryElectricVehicle:
				case VectoSimulationJobType.IEPC_E:
				case VectoSimulationJobType.IEPC_S:
				case VectoSimulationJobType.FCHV:
				case VectoSimulationJobType.FCHV_IEPC:
					return 
						(vehicleData.Components?.ElectricMachines?.Entries
							.Where(x => x.Position != PowertrainPosition.GEN)
							.Sum(x => x.ElectricMachine.R85RatedPower * x.Count) ?? 0.SI<Watt>()) +
						(vehicleData.Components?.IEPC?.R85RatedPower ?? 0.SI<Watt>()) +
						(vehicleData.MaxNetPower1 ?? 0.SI<Watt>());
                case VectoSimulationJobType.Multiple_FCHV:
                case VectoSimulationJobType.Multiple_PEV:
                case VectoSimulationJobType.Multiple_SHEV:
					return
						(vehicleData.Components?.AxlePowertrainInputData?
							.Where(x => x.ElectricMotor != null)
							.Sum(x => x.ElectricMotor.ElectricMachine.R85RatedPower * x.ElectricMotor.Count) ?? 0.SI<Watt>()) +
						(vehicleData.Components?.AxlePowertrainInputData?
							.Where(x => x.IEPCInputData != null)
							.Sum(x => x.IEPCInputData.R85RatedPower) ?? 0.SI<Watt>()) +
						(vehicleData.MaxNetPower1 ?? 0.SI<Watt>());
                default:
					throw new ArgumentOutOfRangeException();
			}
		}

		public static double GetNumberOfPassengers(Mission mission, Meter length, Meter width, double registeredPassengerSeats,
			double registeredPassengersStanding, LoadingType loading)
		{
			var busFloorArea = DeclarationData.BusAuxiliaries.CalculateBusFloorSurfaceArea(length, width);
			var passengerCountRef = busFloorArea * (loading == LoadingType.LowLoading
				? mission.BusParameter.PassengerDensityLow
				: mission.BusParameter.PassengerDensityRef);

			if (loading != LoadingType.ReferenceLoad && loading != LoadingType.LowLoading) {
				throw new VectoException("Unhandled loading type: {0}", loading);
			}

			var passengerCount = registeredPassengerSeats +
								(mission.MissionType == MissionType.Coach ? 0 : registeredPassengersStanding);

			return loading == LoadingType.ReferenceLoad
				? VectoMath.Min(passengerCountRef, passengerCount)
				: VectoMath.Min(passengerCountRef * mission.MissionType.GetLowLoadFactorBus(), passengerCount);
		}

		public static class BusAuxiliaries
		{

			private static IEnvironmentalConditionsMap envMap;

			private static ElectricalConsumerList elUserConfig;

			private static IActuationsMap actuationsMap;
			private static List<SSMTechnology> ssmTechnologies;

			public static readonly JoulePerNormLiter PneumaticSystemElectricDemandPerAirGenerated =
				5600.SI<Watt>() / 325.SI(Unit.SI.NormLiter.Per.Minute).Cast<NormLiterPerSecond>();

			public static ICompressorMap GetCompressorMap(
				IPneumaticSupplyDeclarationData pneumaticSupply)
			{
				var compressorSize = pneumaticSupply.CompressorSize;
				var clutchType = pneumaticSupply.Clutch;

				if (pneumaticSupply.CompressorDrive == CompressorDrive.electrically) {
					return null;
				}

				if (compressorSize == "not applicable") {
					throw new VectoException(
						$"SizeOfAirSupply: '{compressorSize}' invalid for compressor drive: '{pneumaticSupply.CompressorDrive}'");
				}





				var resource = GetCompressorResourceForSize(compressorSize);

				var dragCurveFactorClutch = 1.0;
				switch (clutchType) {
					case "visco":
						dragCurveFactorClutch = Constants.BusAuxiliaries.PneumaticUserConfig.ViscoClutchDragCurveFactor;
						break;
					case "mechanically":
						dragCurveFactorClutch =
							Constants.BusAuxiliaries.PneumaticUserConfig.MechanicClutchDragCurveFactor;
						break;
				}

				return CompressorMapReader.ReadStream(
					RessourceHelper.ReadStream(DeclarationDataResourcePrefix + ".VAUXBus." + resource),
					dragCurveFactorClutch, $"{compressorSize} - {clutchType}");
			}

			private static string GetCompressorResourceForSize(string compressorSize)
			{
				switch (compressorSize) {
					case "Small": return "DEFAULT_1-Cylinder_1-Stage_393ccm.acmp";
					case "Medium Supply 1-stage": return "DEFAULT_1-Cylinder_1-Stage_393ccm.acmp";
					case "Medium Supply 2-stage": return "DEFAULT_2-Cylinder_2-Stage_398ccm.acmp";
					case "Large Supply 1-stage":  return "DEFAULT_2-Cylinder_1-Stage_650ccm.acmp";
					case "Large Supply 2-stage":  return "DEFAULT_3-Cylinder_2-Stage_598ccm.acmp";
					//case "electrically": return "DEFAULT_electrically.acmp";
					default: throw new ArgumentException($"unknown compressor size {compressorSize}", compressorSize);
				}
			}

			public static BusAlternatorTechnologies AlternatorTechnologies = new BusAlternatorTechnologies();
			private static HVACCoolingPower hvacMaxCoolingPower;
			private static HVACHeatingPower hvacMaxHeatingPower;
			private static HeatingDistributionCasesMap heatingDistributionCasesMap;
			private static HeatingDistributionMap heatingDistributionMap;

			public static List<SSMTechnology> SSMTechnologyList =>
				ssmTechnologies ?? (ssmTechnologies = SSMTechnologiesReader.ReadFromStream(
					RessourceHelper.ReadStream(DeclarationDataResourcePrefix + ".Buses.SSMTechList.csv")));

			public static IEnvironmentalConditionsMap DefaultEnvironmentalConditions =>
				envMap ?? (envMap = EnvironmentalContidionsMapReader.ReadStream(
					RessourceHelper.ReadStream(DeclarationDataResourcePrefix + ".Buses.DefaultClimatic.aenv")));

			public static HeatingDistributionCasesMap HeatingDistributionCases =>
				heatingDistributionCasesMap ?? (heatingDistributionCasesMap =
					HeatingDistributionCasesMapReader.ReadStream(
						RessourceHelper.ReadStream(
							DeclarationDataResourcePrefix + ".Buses.HeatingDistributionCases.csv")));

			public static HeatingDistributionMap HeatingDistribution =>
				heatingDistributionMap ?? (heatingDistributionMap = HeatingDistributionMapReader.ReadStream(
					RessourceHelper.ReadStream(DeclarationDataResourcePrefix + ".Buses.HeatingDistribution.csv")));

			public static ElectricalConsumerList DefaultElectricConsumerList =>
				elUserConfig ?? (elUserConfig = ElectricConsumerReader.ReadStream(
					RessourceHelper.ReadStream(DeclarationDataResourcePrefix + ".Buses.ElectricConsumers.csv")));


			public static IActuationsMap ActuationsMap =>
				actuationsMap ?? (actuationsMap = ActuationsMapReader.ReadStream(
					RessourceHelper.ReadStream(DeclarationDataResourcePrefix + ".Buses.DefaultActuationsMap.apac")));

			public static HVACCoolingPower HVACMaxCoolingPower =>
				hvacMaxCoolingPower ?? (hvacMaxCoolingPower = new HVACCoolingPower());

			public static HVACHeatingPower HVACMaxHeatingPower =>
				hvacMaxHeatingPower ?? (hvacMaxHeatingPower = new HVACHeatingPower());

			public static BatteryLimits BatteryLimits { get; } = new BatteryLimits();

			public const double SuperCapUsableCapacity = 0.84;

			public static PerSecond VentilationRate(BusHVACSystemConfiguration? hvacSystemConfig, bool heating)
			{

				switch (hvacSystemConfig) {

					case BusHVACSystemConfiguration.Configuration1:
					case BusHVACSystemConfiguration.Configuration2:
						return Constants.BusAuxiliaries.SteadyStateModel.LowVentilation;

					case BusHVACSystemConfiguration.Configuration3:
					case BusHVACSystemConfiguration.Configuration4:
					case BusHVACSystemConfiguration.Configuration5:
					case BusHVACSystemConfiguration.Configuration6:
					case BusHVACSystemConfiguration.Configuration7:
					case BusHVACSystemConfiguration.Configuration8:
					case BusHVACSystemConfiguration.Configuration9:
					case BusHVACSystemConfiguration.Configuration10:
						return heating
							? Constants.BusAuxiliaries.SteadyStateModel.HighVentilationHeating
							: Constants.BusAuxiliaries.SteadyStateModel.HighVentilation;

					default: throw new ArgumentOutOfRangeException(nameof(hvacSystemConfig), hvacSystemConfig, null);
				}
			}

			public static SquareMeter CalculateBusFloorSurfaceArea(Meter busLength, Meter busWidth)
			{
				return (busLength - Constants.BusParameters.DriverCompartmentLength) * CorrectedBusWidth(busWidth);
			}

			public static Meter CorrectedBusWidth(Meter busWidth)
			{
				return busWidth.IsBetween(Constants.BusParameters.VehicleWidthLow,
					Constants.BusParameters.VehicleWidthHigh)
					? Constants.BusParameters.VehicleWidthHigh
					: busWidth;
			}


			public static Meter CalculateInternalLength(Meter vehicleLength, VehicleCode? vehicleCode,
				double numPassSeatsLowerDeck)
			{
				if (vehicleCode.GetFloorType() == FloorType.LowFloor) {
					return vehicleCode.IsDoubleDeckerBus() ? 2 * vehicleLength : vehicleLength;
				}

				if (vehicleCode.GetFloorType() == FloorType.HighFloor) {
					if (vehicleCode.IsDoubleDeckerBus()) {
						return numPassSeatsLowerDeck > 6 ? 1.5 * vehicleLength : vehicleLength + 2.4.SI<Meter>();
					}

					return vehicleLength;
				}

				throw new VectoException("Internal Length for floorType {0} {1} not defined",
					vehicleCode.GetFloorType().ToString(), vehicleCode.IsDoubleDeckerBus() ? "DD" : "SD");
			}

			public static Meter CalculateLengthInteriorLights(
				Meter vehicleLength, VehicleCode? vehicleCode, double numPassLowFloor)
			{
				return CalculateInternalLength(vehicleLength, vehicleCode, numPassLowFloor);
			}

			public static Meter CalculateInternalHeight(VehicleCode? vehicleCode, RegistrationClass? registrationClass,
				Meter bodyHeight)
			{
				if (vehicleCode.IsDoubleDeckerBus()) {
					return Constants.BusParameters.InternalHeightDoubleDecker;
				}

				switch (vehicleCode.GetFloorType()) {
					case FloorType.LowFloor:
						return bodyHeight;
					case FloorType.HighFloor:
						if ((registrationClass == RegistrationClass.II_III && bodyHeight > 3.1.SI<Meter>()) ||
							registrationClass == RegistrationClass.III || registrationClass == RegistrationClass.B) {
							return Constants.BusParameters.InternalHeightDoubleDecker;
						}

						return bodyHeight - Constants.BusParameters.HeightLuggageCompartment;
				}

				throw new VectoException("Internal height for vehicle floor type '{0}' {1} not defined",
					vehicleCode.GetFloorType().ToString(),
					vehicleCode.IsDoubleDeckerBus() ? "double decker" : "single decker");
			}

			public static Meter WindowHeight(bool doubleDecker)
			{
				return doubleDecker
					? Constants.BusParameters.WindowHeightDoubleDecker
					: Constants.BusParameters.WindowHeightSingleDecker;
			}

			public static SquareMeter FrontAndRearWindowArea(bool doubleDecker)
			{
				return doubleDecker
					? Constants.BusParameters.FrontAndRearWindowAreaDoubleDecker
					: Constants.BusParameters.FrontAndRearWindowAreaSingleDecker;
			}

			public static WattPerKelvinSquareMeter UValue(FloorType floorType)
			{
				switch (floorType) {
					case FloorType.LowFloor:
						return 4.SI<WattPerKelvinSquareMeter>();
					case FloorType.SemiLowFloor:
						return 3.5.SI<WattPerKelvinSquareMeter>();
					case FloorType.HighFloor:
						return 3.SI<WattPerKelvinSquareMeter>();
					default: throw new ArgumentOutOfRangeException(nameof(floorType), floorType, null);
				}
			}

			public static double CalculateCOP(Watt coolingPwrDriver, double copDriver, Watt coolingPwrPass,
				double copPass)
			{
				if (coolingPwrDriver.IsGreater(0) && copDriver.IsEqual(0)) {
					copDriver = copPass;
				}

				if (coolingPwrDriver.IsEqual(0) && coolingPwrPass.IsEqual(0)) {
					return 1.0;
				}

				return (coolingPwrDriver * copDriver + coolingPwrPass * copPass) /
						(coolingPwrDriver + coolingPwrPass);
			}

			public static Meter CorrectionLengthDrivetrainVolume(VehicleCode? vehicleCode, bool? lowEntry, int numAxles,
				bool articulated)
			{
				if ((vehicleCode == VehicleCode.CE || vehicleCode == VehicleCode.CG) && (bool)lowEntry) {
					switch (numAxles) {
						case 2: return 1.0.SI<Meter>();
						case 3: return articulated ? 1.0.SI<Meter>() : 1.25.SI<Meter>();
						case 4: return 1.25.SI<Meter>();
						default: throw new VectoException("invalid number of axles {0}", numAxles);
					}
				}

				return 0.SI<Meter>();
			}

			public static BusHVACSystemConfiguration GetHVACConfig(BusHVACSystemConfiguration hvacConfigurationInput,
				HeatPumpType heatPumpDriver, HeatPumpType heatPumpPassenger)
			{
				var hasDriverHP = !heatPumpDriver.IsOneOf(HeatPumpType.none, HeatPumpType.not_applicable);
				var hasPassengerHP = heatPumpPassenger != HeatPumpType.none;

				switch (hvacConfigurationInput) {
					case BusHVACSystemConfiguration.Unknown:
					case BusHVACSystemConfiguration.Configuration0:
						throw new VectoException($"Invalid HVAC Configuration {hvacConfigurationInput}");

					case BusHVACSystemConfiguration.Configuration1 when !hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration1;

					case BusHVACSystemConfiguration.Configuration2 when !hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration1;
					case BusHVACSystemConfiguration.Configuration2 when hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration2;

					case BusHVACSystemConfiguration.Configuration3 when !hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration3;

					case BusHVACSystemConfiguration.Configuration4 when !hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration3;
					case BusHVACSystemConfiguration.Configuration4 when hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration4;

					case BusHVACSystemConfiguration.Configuration5 when !hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration3;
					case BusHVACSystemConfiguration.Configuration5 when !hasDriverHP && hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration5;

					case BusHVACSystemConfiguration.Configuration6 when !hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration3;
					case BusHVACSystemConfiguration.Configuration6 when !hasDriverHP && hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration6;

					case BusHVACSystemConfiguration.Configuration7 when !hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration3;
					case BusHVACSystemConfiguration.Configuration7 when hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration4;
					case BusHVACSystemConfiguration.Configuration7 when !hasDriverHP && hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration5;
					case BusHVACSystemConfiguration.Configuration7 when hasDriverHP && hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration7;

					case BusHVACSystemConfiguration.Configuration8 when !hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration3;
					case BusHVACSystemConfiguration.Configuration8 when !hasDriverHP && hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration8;

					case BusHVACSystemConfiguration.Configuration9 when !hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration3;
					case BusHVACSystemConfiguration.Configuration9 when hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration4;
					case BusHVACSystemConfiguration.Configuration9 when !hasDriverHP && hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration8;
					case BusHVACSystemConfiguration.Configuration9 when hasDriverHP && hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration9;

					case BusHVACSystemConfiguration.Configuration10 when !hasDriverHP && !hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration3;
					case BusHVACSystemConfiguration.Configuration10 when !hasDriverHP && hasPassengerHP:
						return BusHVACSystemConfiguration.Configuration10;
				}

				throw new VectoException(
					$"Invalid HVAC combination! System Configuration: {hvacConfigurationInput.GetName()}, Driver HeatPump: {heatPumpDriver.GetLabel()}, Passenger HeatPump: {heatPumpPassenger.GetLabel()}");
			}

			public static WattSecond CalculateBatteryCapacity(
				IList<IBusAuxElectricStorageDeclarationInputData> electricStorage)
			{
				if (electricStorage == null) {
					return null;
				}

				var batteries = electricStorage.Where(x => x is BusAuxBatteryInputData)
					.Cast<BusAuxBatteryInputData>().ToArray();
				var supercaps = electricStorage.Where(x => x is BusAuxCapacitorInputData)
					.Cast<BusAuxCapacitorInputData>().ToArray();

				var batteryCapacity = 0.SI<WattSecond>();
				var capacitorCapacity = 0.SI<WattSecond>();
				if (batteries.Any()) {
					var sumU = batteries.Sum(b => b.Voltage);
					var minCap = batteries.Min(b =>
						b.Capacity * DeclarationData.BusAuxiliaries.BatteryLimits.Lookup(b.Technology).SoC_Range);
					batteryCapacity = minCap * sumU;
				}

				if (supercaps.Any()) {
					var minCap = supercaps.MinBy(c => c.Capacity);
					var sumCap = supercaps.Sum(c => minCap.Capacity / c.Capacity);
					capacitorCapacity = minCap.Capacity * minCap.Voltage * minCap.Voltage * 0.5 * sumCap *
										DeclarationData.BusAuxiliaries.SuperCapUsableCapacity;
				}

				return batteryCapacity + capacitorCapacity;
			}




			public static Watt CalculateMaxAlternatorPower(IElectricSupplyDeclarationData electricSupply)
			{
				var maxElectricPower = electricSupply.ElectricStorage.Where(x => x is BusAuxBatteryInputData)
					.Cast<BusAuxBatteryInputData>()
					.Sum(b => b.Capacity * DeclarationData.BusAuxiliaries.BatteryLimits.Lookup(b.Technology).C_Rate *
							b.Voltage);
				if (electricSupply.ElectricStorage.Any(x => x is BusAuxCapacitorInputData)) {
					maxElectricPower = null;
				}

				var maxAlternatorPower =
					VectoMath.Min(electricSupply.Alternators.Sum(x => x.RatedVoltage * x.RatedCurrent),
						maxElectricPower);
				return maxAlternatorPower;
			}

		}

		public static class Driver
		{
			public static class LookAhead
			{
				public const bool Enabled = true;

				public const double DecisionFactorCoastingOffset = 2.5;
				public const double DecisionFactorCoastingScaling = 1.5;
				public const double LookAheadDistanceFactor = 10;
				public static readonly MeterPerSecond MinimumSpeed = 50.KMPHtoMeterPerSecond();
			}

			public static class OverSpeed
			{
				public static readonly MeterPerSecond MinSpeed = 50.KMPHtoMeterPerSecond();
				public static readonly MeterPerSecond AllowedOverSpeed = 2.5.KMPHtoMeterPerSecond();
			}

			public interface IEngineStopStart {
				Second ActivationDelay { get; }
				Second MaxEngineOffTimespan { get; }
				double UtilityFactor   { get; } 
			}
			private class EngineStopStartLorry : IEngineStopStart
			{
				public Second ActivationDelay => 2.SI<Second>();
				public Second MaxEngineOffTimespan => 120.SI<Second>();
				public double UtilityFactor => 0.8;
			}

			private class EngineStopStartBus : IEngineStopStart
			{
				private const double ConventionalUF = 0.35;
				private const double HybridElectrifiedCompressorUF = 0.65;
				private const double HybridUF = 0.55;

				public EngineStopStartBus(VectoSimulationJobType simType, CompressorDrive compressorDrive, ArchitectureID arch)
				{
					if (simType == VectoSimulationJobType.ConventionalVehicle) {
						arch = ArchitectureID.UNKNOWN;
					}

					_jobType = simType;
					_compressorDrive = compressorDrive;
					_arch = arch;

					if (_jobType == VectoSimulationJobType.ConventionalVehicle)
					{
						// P0 ???
						UtilityFactor = ConventionalUF;
					} else {
						if (_compressorDrive == CompressorDrive.electrically) {
							UtilityFactor = HybridElectrifiedCompressorUF;
						} else {
							UtilityFactor = HybridUF;
						}
					}
				}
				private CompressorDrive _compressorDrive;
				private ArchitectureID _arch;
				private readonly VectoSimulationJobType _jobType;
				public Second ActivationDelay => 2.SI<Second>();
				public Second MaxEngineOffTimespan => 120.SI<Second>();
				public double UtilityFactor { get; }
			}


			public static IEngineStopStart GetEngineStopStartLorry()
			{
				return new EngineStopStartLorry();
			}

			/// <summary>
			/// 
			/// </summary>
			/// <param name="hdvClass"></param>
			/// <param name="jobType">only used for buses</param>
			/// <param name="arch">only used for buses</param>
			/// <param name="compressorDrive">only used for buses</param>
			/// <returns></returns>
			public static IEngineStopStart GetEngineStopStart(VehicleClass hdvClass, VectoSimulationJobType? jobType = null,  ArchitectureID? arch = null,
				CompressorDrive? compressorDrive = null)
			{

				if (hdvClass.IsBus()) {
					return GetEngineStopStartBus(jobType.Value, arch.Value, compressorDrive.Value);
				} else {
					return new EngineStopStartLorry();
				}
			}

			public static IEngineStopStart GetEngineStopStartBus(VectoSimulationJobType jobType, ArchitectureID arch, CompressorDrive compressorDrive)
			{
				return new EngineStopStartBus(jobType, compressorDrive, arch);
			}

			public static class EcoRoll
			{
				public static readonly MeterPerSecond MinSpeed = 60.KMPHtoMeterPerSecond();
				public static readonly Second ActivationDelay = 2.SI<Second>();
				public static readonly MeterPerSecond UnderspeedThreshold = 0.KMPHtoMeterPerSecond();

				public static readonly MeterPerSquareSecond AccelerationLowerLimit = 0.SI<MeterPerSquareSecond>();
				public static readonly MeterPerSquareSecond AccelerationUpperLimit = 0.1.SI<MeterPerSquareSecond>();
			}

			public static class PCC
			{
				public static readonly MeterPerSecond PCCEnableSpeed = 80.KMPHtoMeterPerSecond();
				public static readonly MeterPerSecond MinSpeed = 50.KMPHtoMeterPerSecond();
				public static readonly Meter PreviewDistanceUseCase1 = 1500.SI<Meter>();
				public static readonly Meter PreviewDistanceUseCase2 = 1000.SI<Meter>();
				public static readonly MeterPerSecond Underspeed = 8.KMPHtoMeterPerSecond();
				public static readonly MeterPerSecond OverspeedUseCase3 = 5.KMPHtoMeterPerSecond();
			}
		}

		public static class Trailer
		{
			public const double RollResistanceCoefficient = 0.0055;
			public const string FuelEfficiencyClass = "X";
			public const double TyreTestLoad = 37500;

			public const bool TwinTyres = false;

			//public const string WheelsType = "385/65 R 22.5";
		}

		public static class Engine
		{
			public static readonly KilogramSquareMeter ClutchInertia = 1.3.SI<KilogramSquareMeter>();
			public static readonly KilogramSquareMeter TorqueConverterInertia = 1.2.SI<KilogramSquareMeter>();

			public static readonly KilogramSquareMeter EngineBaseInertia = 0.41.SI<KilogramSquareMeter>();
			public static readonly KilogramPerMeter EngineDisplacementInertia = 270.SI<KilogramPerMeter>();
			public static readonly Second DefaultEngineStartTime = 1.SI<Second>();

			public const double TorqueLimitGearboxFactor = 0.9;
			public const double TorqueLimitVehicleFactor = 0.95;

			public static readonly SI SmallEnginesBound = 3.2.SI<Liter>().Cast<CubicMeter>();
			public static readonly SI MidEnginesBound = 5.SI<Liter>().Cast<CubicMeter>();

			public static readonly KilogramSquareMeter ManualBaseInertia = 1.885.SI<KilogramSquareMeter>();
			public static readonly KilogramSquareMeter ATBaseInertia = 1.707.SI<KilogramSquareMeter>();

			public static readonly KilogramPerMeter SmallEngineDisplacementInertia = 400.SI<KilogramPerMeter>();
			public static readonly KilogramPerMeter MidEngineATDisplacementInertia = 933.SI<KilogramPerMeter>();
			public static readonly KilogramPerMeter MidEngineManualDisplacementInertia = 989.SI<KilogramPerMeter>();

			public static KilogramSquareMeter EngineInertia(VectoSimulationJobType jobType, CubicMeter displacement, GearboxType? gbxType)
			{
				if (displacement <= SmallEnginesBound) {
					return ComputeSmallEngineInertia(displacement);
				}
				else if ((displacement > SmallEnginesBound) && (displacement <= MidEnginesBound)) {
					return ComputeMidEngineInertia(displacement, gbxType);
				}
				else {
					return ComputeBigEngineInertia(jobType, displacement, gbxType);
				}
			}

			private static KilogramSquareMeter ComputeSmallEngineInertia(CubicMeter displacement)
			{ 
				return (SmallEngineDisplacementInertia * displacement).Cast<KilogramSquareMeter>();
			}

			private static KilogramSquareMeter ComputeMidEngineInertia(CubicMeter displacement, GearboxType? gbxType)
			{ 
				if (!gbxType.HasValue) {
					throw new VectoException("Gearbox type must be provided!");
				}

				return gbxType.Value.AutomaticTransmission()
					? (MidEngineATDisplacementInertia * displacement) - ATBaseInertia
					: (MidEngineManualDisplacementInertia * displacement) - ManualBaseInertia;
			}

			private static KilogramSquareMeter ComputeBigEngineInertia(VectoSimulationJobType jobType, CubicMeter displacement, GearboxType? gbxType)
			{
				// VB Code:    Return 1.3 + 0.41 + 0.27 * (Displ / 1000)
				KilogramSquareMeter clutchPlateTc;
				if (jobType.IsOneOf(VectoSimulationJobType.SerialHybridVehicle, VectoSimulationJobType.IEPC_S)) {
					clutchPlateTc = 0.SI<KilogramSquareMeter>();
				} else {
					if (!gbxType.HasValue) {
						throw new VectoException("Gearbox type must be provided!");
					}
					clutchPlateTc = (gbxType.Value.AutomaticTransmission() ? TorqueConverterInertia : ClutchInertia);
				}

				return clutchPlateTc + EngineBaseInertia +
						EngineDisplacementInertia * displacement;
			}
		}

		public static class GearboxTCU
		{

			public static readonly MeterPerSecond MIN_SPEED_AFTER_TRACTION_INTERRUPTION = 5.KMPHtoMeterPerSecond();

			public const double TorqueReserve = 0;
			public const double TorqueReserveStart = 0.2;

			public static readonly MeterPerSecond StartSpeed = 8.KMPHtoMeterPerSecond();
			public static readonly MeterPerSquareSecond StartAcceleration = 0.8.SI<MeterPerSquareSecond>();


			public static double RatingFactorCurrentGear = 0.97;
			public static double RatingFactorCurrentGearAT = 0.97;

			public static double VelocityDropFactor = 1.0;
			public static double AccelerationFactor = 0.5;

			public static double RatioEarlyUpshiftFC = 24;
			public static double RatioEarlyDownshiftFC = 24;

			public static int AllowedGearRangeFCAMT = 2;
			public static int AllowedGearRangeFCAT = 1;
			public static int AllowedGearRangeFCATSkipGear = 2;
			public static int ATSkipGearsThreshold = 6;

			public static PerSecond MinEngineSpeedPostUpshift = 0.RPMtoRad();

			public static Second ATLookAheadTime = 1.5.SI<Second>(); //Gearbox.PowershiftShiftTime;

			public static double[] LoadStageThresholdsUp = { 19.7, 36.34, 53.01, 69.68, 86.35 };
			public static double[] LoadStageThresoldsDown = { 13.7, 30.34, 47.01, 63.68, 80.35 };

			public static double[][] ShiftSpeedsTCToLocked = {
				new[] {  90.0, 120, 165,  90, 120, 165 },
				new[] {  90.0, 120, 165,  90, 120, 165 },
				new[] {  90.0, 120, 165,  90, 120, 165 },
				new[] {  90.0, 120, 165, 110, 140, 185 },
				new[] { 100.0, 130, 175, 120, 150, 195 },
				new[] { 110.0, 140, 185, 130, 160, 205 },
			};

			public const double DownhillSlope = -5;
			public const double UphillSlope = 5;

			public const double DragMarginFactor = 0.7;


			// TODO: MQ 2019-11-26 remove, once the parameters are fixed! make fields above read-only or const
			static GearboxTCU()
			{
				//#if RELEASE_CANDIDATE
				var expectedFile = @"Declaration\EffShiftParameters.vtcu";
				if (!File.Exists(expectedFile)) {
					return;
				}

				var tcuData = JSONInputDataFactory.ReadShiftParameters(expectedFile, true);
				if (tcuData.RatingFactorCurrentGear.HasValue) {
					RatingFactorCurrentGear = tcuData.RatingFactorCurrentGear.Value;
					RatingFactorCurrentGearAT = tcuData.RatingFactorCurrentGear.Value;
				}
				if (tcuData.RatioEarlyDownshiftFC.HasValue) {
					RatioEarlyDownshiftFC = tcuData.RatioEarlyDownshiftFC.Value;
				}
				if (tcuData.RatioEarlyUpshiftFC.HasValue) {
					RatioEarlyUpshiftFC = tcuData.RatioEarlyUpshiftFC.Value;
				}
				if (tcuData.AllowedGearRangeFC.HasValue) {
					AllowedGearRangeFCAMT = tcuData.AllowedGearRangeFC.Value;
					AllowedGearRangeFCAT = tcuData.AllowedGearRangeFC.Value;
				}
				if (tcuData.VeloictyDropFactor.HasValue) {
					VelocityDropFactor = tcuData.VeloictyDropFactor.Value;
				}
				if (tcuData.AccelerationFactor.HasValue) {
					AccelerationFactor = tcuData.AccelerationFactor.Value;
				}
				if (tcuData.ATLookAheadTime != null) {
					ATLookAheadTime = tcuData.ATLookAheadTime;
				}
				if (tcuData.LoadStageThresholdsDown != null && LoadStageThresoldsDown.Length > 0) {
					LoadStageThresoldsDown = tcuData.LoadStageThresholdsDown.ToArray();
				}
				if (tcuData.LoadStageThresholdsUp != null && LoadStageThresholdsUp.Length > 0) {
					LoadStageThresholdsUp = tcuData.LoadStageThresholdsUp.ToArray();
				}
				if (tcuData.ShiftSpeedsTCToLocked != null && ShiftSpeedsTCToLocked.Length > 0) {
					ShiftSpeedsTCToLocked = tcuData.ShiftSpeedsTCToLocked;
				}
				if (tcuData.MinEngineSpeedPostUpshift != null) {
					MinEngineSpeedPostUpshift = tcuData.MinEngineSpeedPostUpshift;
				}
				//#endif
			}
		}

		public static class Gearbox
		{
			public static readonly KilogramSquareMeter Inertia = 0.SI<KilogramSquareMeter>();

			public static readonly MeterPerSecond TruckMaxAllowedSpeed = 85.KMPHtoMeterPerSecond();
			public const double ShiftPolygonRPMMargin = 7; // %
			private const double ShiftPolygonEngineFldMargin = 0.98;

			public static readonly Second MinTimeBetweenGearshifts = 2.SI<Second>();
			public static readonly Second DownshiftAfterUpshiftDelay = 6.SI<Second>();
			public static readonly Second UpshiftAfterDownshiftDelay = 6.SI<Second>();

			public static readonly MeterPerSquareSecond UpshiftMinAcceleration = 0.1.SI<MeterPerSquareSecond>();

			//public static readonly PerSecond TorqueConverterSpeedLimit = 1600.RPMtoRad();
			public static double TorqueConverterSecondGearThreshold(VehicleCategory category)
			{
				return category.IsLorry() ? 1.8 : 1.85;
			}

			public static readonly Second PowershiftShiftTime = 0.8.SI<Second>();

			/// <summary>
			/// computes the shift polygons for a single gear according to the whitebook 2016
			/// </summary>
			/// <param name="type"></param>
			/// <param name="gearIdx">index of the gear to compute the shift polygons for  -- gear number - 1!</param>
			/// <param name="fullLoadCurve">engine full load curve, potentially limited by the gearbox</param>
			/// <param name="gears">list of gears</param>
			/// <param name="engine">engine data</param>
			/// <param name="axlegearRatio"></param>
			/// <param name="dynamicTyreRadius"></param>
			/// <param name="electricMotorData"></param>
			/// <returns></returns>
			public static ShiftPolygon ComputeShiftPolygon(
				GearboxType type, int gearIdx, EngineFullLoadCurve fullLoadCurve,
				IList<ITransmissionInputData> gears, CombustionEngineData engine, double axlegearRatio, Meter dynamicTyreRadius, ElectricMotorData electricMotorData)
			{
				switch (type) {
					case GearboxType.AMT:
					case GearboxType.APTN:
					case GearboxType.IHPC:
						// TODO MQ: 2020-10-14: compute for AMT with ICE and AMT with EM differently
						return ComputeEfficiencyShiftPolygon(gearIdx, fullLoadCurve, gears, engine, axlegearRatio, dynamicTyreRadius);
					case GearboxType.MT:
						return ComputeManualTransmissionShiftPolygon(
							gearIdx, fullLoadCurve, gears, engine, axlegearRatio, dynamicTyreRadius);
					case GearboxType.ATSerial:
					case GearboxType.ATPowerSplit:
						return TorqueConverter.ComputeShiftPolygon(fullLoadCurve, gearIdx == 0, gearIdx >= gears.Count - 1);
					default: throw new ArgumentOutOfRangeException(nameof(type), type, null);
				}

			}
			
			
			public static ShiftPolygon ComputeElectricMotorShiftPolygon(
				int gearIdx, 
				ElectricMotorData electricMotorData,
				IList<ITransmissionInputData> gears, 
				double? downshiftMaxSpeedFactor = null,
				double? downShiftMinSpeedFactor = null)
			{
				if ((downshiftMaxSpeedFactor != null && !downshiftMaxSpeedFactor.Value.IsBetween(0.0, 1.0)) ||
					downShiftMinSpeedFactor != null && !downShiftMinSpeedFactor.Value.IsBetween(0.0, 1.0)) {
					throw new VectoException("Invalid downshift factors: must be between 0.0 and 1.0");
				}
				
				//EM FullloadCurve
				var voltageLevelData = electricMotorData.EfficiencyData.VoltageLevels.First();
                var fullLoadCurveOrig = (voltageLevelData is IEPCVoltageLevelData iepc) && (iepc.FullLoadCurves.Count() > 0)
                    ? iepc.FullLoadCurves[(uint)gears[gearIdx].Gear]
                    : voltageLevelData.FullLoadCurve;

                var emRatio = electricMotorData.RatioADC;
				var lossMap = electricMotorData.TransmissionLossMap;
				var emMaxSpeed = electricMotorData.EfficiencyData.MaxSpeed;
				
				//Transform EM Fullloadcurve to include ADC losses and ratio. Convert EM to Drivetrain
				var fullLoadCurveTransformed = lossMap == null
					? fullLoadCurveOrig
					: TransformFullLoadCurve(fullLoadCurveOrig, lossMap, emRatio);
				var emMaxSpeedDt = emMaxSpeed / emRatio;
				
				
				//From now on we are on the gbx_in side.
				var gbxMaxTq = gears[gearIdx].MaxTorque != null ? gears[gearIdx].MaxTorque : null;
				var gbxMaxSpeed = gears[gearIdx].MaxInputSpeed != null ? gears[gearIdx].MaxInputSpeed : null;
				
				
				var fullLoadCurve = gbxMaxTq == null
					? fullLoadCurveTransformed
					: LimitElectricMotorFullLoadCurve(fullLoadCurveTransformed, gbxMaxTq);
				
				if (gears.Count < 2) {
					throw new VectoException("ComputeShiftPolygon needs at least 2 gears. {0} gears given.", gears.Count);
				}
			
				var downShift = new List<ShiftPolygon.ShiftPolygonEntry>();
				var upShift = new List<ShiftPolygon.ShiftPolygonEntry>();
				if (gearIdx > 0) {
					var nMax = downshiftMaxSpeedFactor.HasValue
						? downshiftMaxSpeedFactor.Value * fullLoadCurve.RatedSpeed
						: fullLoadCurve.NP80low;
					
					var nMin = downShiftMinSpeedFactor.HasValue 
						? downShiftMinSpeedFactor.Value * fullLoadCurve.RatedSpeed
						: fullLoadCurve.RatedSpeed * 0.1;
					
					downShift.AddRange(DownshiftLineDrive(fullLoadCurve, fullLoadCurveTransformed, nMin, fullLoadCurve.NP80low));
					downShift.AddRange(DownshiftLineDrag(fullLoadCurve, fullLoadCurveTransformed, nMin, nMax));
			
				}
				if (gearIdx >= gears.Count - 1) {
					return new ShiftPolygon(TransformShiftPolygonEntries(downShift), TransformShiftPolygonEntries(upShift));
				}
			
				upShift.Add(new ShiftPolygon.ShiftPolygonEntry(fullLoadCurve.MaxGenerationTorque * 1.1, VectoMath.Min(emMaxSpeedDt, gbxMaxSpeed) * 0.9));
				upShift.Add(new ShiftPolygon.ShiftPolygonEntry(fullLoadCurve.MaxDriveTorque * 1.1, VectoMath.Min(emMaxSpeedDt, gbxMaxSpeed) * 0.9));
				return new ShiftPolygon(TransformShiftPolygonEntries(downShift), TransformShiftPolygonEntries(upShift));
			}


			/// <summary>
			/// Transforms the shiftpolygons. The shift polygons are calculated based on the EM,
			/// to use them with gearbox input torque we need to invert the sign of the torque entries.
			/// </summary>
			/// <param name="entries"></param>
			/// <returns></returns>
			private static IList<ShiftPolygon.ShiftPolygonEntry> TransformShiftPolygonEntries(
				IList<ShiftPolygon.ShiftPolygonEntry> entries)
			{
				foreach (var entry in entries) {
					entry.Torque = entry.Torque * (-1);
				}

				return entries.Reverse().ToList();
			}

			private static ElectricMotorFullLoadCurve TransformFullLoadCurve(ElectricMotorFullLoadCurve emFld,
				TransmissionLossMap lossMap, double ratioAdc)
			{
				var fldCurve =
					new ElectricMotorFullLoadCurve(
						emFld.FullLoadEntries.Select(e => {
								var drive = lossMap.GetOutTorqueAndSpeed(e.MotorSpeed, e.FullDriveTorque);
								var generation = lossMap.GetOutTorqueAndSpeed(e.MotorSpeed, e.FullGenerationTorque);
								return new ElectricMotorFullLoadCurve.FullLoadEntry() {
									FullDriveTorque = drive.outTorque,
									FullGenerationTorque = generation.outTorque,
									MotorSpeed = drive.outAngularVelocity
								};
							}
						).ToList());
				
				return fldCurve;
			}
			
			/// <summary>
			/// Limit the fullload curve to the max gearbox in torque
			/// </summary>
			/// <param name="emFld"></param>
			/// <param name="maxTq"></param>
			/// <returns></returns>
			public static ElectricMotorFullLoadCurve LimitElectricMotorFullLoadCurve(ElectricMotorFullLoadCurve emFld, NewtonMeter maxTq)
			{
				var contTqFld = new ElectricMotorFullLoadCurve(new List<ElectricMotorFullLoadCurve.FullLoadEntry>() {
					new ElectricMotorFullLoadCurve.FullLoadEntry() {
						MotorSpeed = 0.RPMtoRad(),
						FullDriveTorque = -maxTq,
						FullGenerationTorque = maxTq
					},
					new ElectricMotorFullLoadCurve.FullLoadEntry() {
						MotorSpeed = 1.1 * emFld.MaxSpeed,
						FullDriveTorque = -maxTq,
						FullGenerationTorque = maxTq
					}
				});
				var limitedFld = AbstractSimulationDataAdapter.IntersectEMFullLoadCurves(emFld, contTqFld);
				
				return limitedFld;
			}

			private static List<ShiftPolygon.ShiftPolygonEntry> DownshiftLineDrive(
				ElectricMotorFullLoadCurve fullLoadCurve, ElectricMotorFullLoadCurve fullLoadCurveOrig,
				PerSecond nMin, PerSecond nMax)
			{
				var retVal = new List<ShiftPolygon.ShiftPolygonEntry>();
				var downShiftPoints = fullLoadCurve
					.FullLoadEntries.Where(fldEntry => fldEntry.MotorSpeed >= nMin && fldEntry.MotorSpeed <= nMax)
					.Select(
						fldEntry =>
							new Point(fldEntry.MotorSpeed.Value(), fldEntry.FullDriveTorque.Value() * ShiftPolygonEngineFldMargin))
					.ToList();
				//retVal.Add(new ShiftPolygon.ShiftPolygonEntry(fullLoadCurve.MaxDriveTorque * 1.1, nMax));
				if (downShiftPoints.Count == 0) {
					// coarse grid points in FLD
					retVal.Add(
						new ShiftPolygon.ShiftPolygonEntry(
							fullLoadCurveOrig.MaxDriveTorque * 1.1,
							nMax));
					retVal.Add(
						new ShiftPolygon.ShiftPolygonEntry(
							fullLoadCurve.FullLoadDriveTorque(nMax) * ShiftPolygonEngineFldMargin,
							nMax));
					retVal.Add(
						new ShiftPolygon.ShiftPolygonEntry(
							fullLoadCurve.FullLoadDriveTorque(nMin) * ShiftPolygonEngineFldMargin,
							nMin));

				} else {
					retVal.Add(
						new ShiftPolygon.ShiftPolygonEntry(
							fullLoadCurveOrig.MaxDriveTorque * 1.1,
							nMax));
					if (downShiftPoints.Max(x => x.X) < nMax) {
						retVal.Add(
							new ShiftPolygon.ShiftPolygonEntry(
								fullLoadCurve.FullLoadDriveTorque(nMax) * ShiftPolygonEngineFldMargin,
								nMax));
					}

					retVal.AddRange(
						downShiftPoints.Select(
							x => new ShiftPolygon.ShiftPolygonEntry(
								x.Y.SI<NewtonMeter>(), x.X.SI<PerSecond>())).OrderByDescending(x => x.AngularSpeed.Value()));
					if (downShiftPoints.Min(x => x.X) > nMin) {
						retVal.Add(
							new ShiftPolygon.ShiftPolygonEntry(
								fullLoadCurve.FullLoadDriveTorque(nMin) * ShiftPolygonEngineFldMargin,
								nMin));
					}
				}

				return retVal;
			}

			private static List<ShiftPolygon.ShiftPolygonEntry> DownshiftLineDrag(
				ElectricMotorFullLoadCurve fullLoadCurve, ElectricMotorFullLoadCurve fullLoadCurveOrig,
				PerSecond nMin, PerSecond nMax)
			{
				var retVal = new List<ShiftPolygon.ShiftPolygonEntry>();
				var downShiftPoints = fullLoadCurve
					.FullLoadEntries.Where(fldEntry => fldEntry.MotorSpeed >= nMin && fldEntry.MotorSpeed <= nMax)
					.Select(
						fldEntry =>
							new Point(fldEntry.MotorSpeed.Value(), fldEntry.FullGenerationTorque.Value() * ShiftPolygonEngineFldMargin))
					.ToList();
				//retVal.Add(new ShiftPolygon.ShiftPolygonEntry(fullLoadCurve.MaxGenerationTorque * 1.1, nMax));
				if (downShiftPoints.Count == 0) {
					// coarse grid points in FLD
					retVal.Add(
						new ShiftPolygon.ShiftPolygonEntry(
							fullLoadCurve.FullGenerationTorque(nMin) * ShiftPolygonEngineFldMargin,
							nMin));
					retVal.Add(
						new ShiftPolygon.ShiftPolygonEntry(
							fullLoadCurve.FullGenerationTorque(nMax) * ShiftPolygonEngineFldMargin,
							nMax));
					retVal.Add(
						new ShiftPolygon.ShiftPolygonEntry(
							fullLoadCurveOrig.MaxGenerationTorque * 1.1,
							nMax));
				} else {
					if (downShiftPoints.Min(x => x.X) > nMin) {
						retVal.Add(
							new ShiftPolygon.ShiftPolygonEntry(
								fullLoadCurve.FullGenerationTorque(nMin) * ShiftPolygonEngineFldMargin,
								nMin));
					}

					retVal.AddRange(
						downShiftPoints.Select(
							x => new ShiftPolygon.ShiftPolygonEntry(
								x.Y.SI<NewtonMeter>(), x.X.SI<PerSecond>())));
					if (downShiftPoints.Max(x => x.X) < nMax) {
						retVal.Add(
							new ShiftPolygon.ShiftPolygonEntry(
								fullLoadCurve.FullGenerationTorque(nMax) * ShiftPolygonEngineFldMargin,
								nMax));
					}
					retVal.Add(
						new ShiftPolygon.ShiftPolygonEntry(
							fullLoadCurveOrig.MaxGenerationTorque * 1.1,
							nMax));
				}

				return retVal;
			}

			public static ShiftPolygon ComputeEfficiencyShiftPolygon(
				int gearIdx, EngineFullLoadCurve fullLoadCurve, IList<ITransmissionInputData> gears, CombustionEngineData engine,
				double axlegearRatio, Meter dynamicTyreRadius)
			{
				if (gears.Count < 2) {
					throw new VectoException("ComputeShiftPolygon needs at least 2 gears. {0} gears given.", gears.Count);
				}

				var clutchClosingSpeed = (engine.FullLoadCurves[0].RatedSpeed - engine.IdleSpeed) *
									Constants.SimulationSettings.ClutchClosingSpeedNorm + engine.IdleSpeed;

				var p2 = new Point(Math.Min((clutchClosingSpeed - 10.RPMtoRad()).Value(), engine.IdleSpeed.Value() * 1.1), 0);
				var p3 = new Point(fullLoadCurve.NTq99lSpeed.Value(), 0);
				var p5 = new Point(fullLoadCurve.NP98hSpeed.Value(), fullLoadCurve.MaxTorque.Value() * 1.1);

				var downShift = new List<ShiftPolygon.ShiftPolygonEntry>();

				if (gearIdx > 0) {
					var downShiftPoints = fullLoadCurve
						.FullLoadEntries.Where(fldEntry => fldEntry.EngineSpeed >= p2.X && fldEntry.EngineSpeed <= p3.X)
						.Select(
							fldEntry =>
								new Point(fldEntry.EngineSpeed.Value(), fldEntry.TorqueFullLoad.Value() * ShiftPolygonEngineFldMargin))
						.ToList();
					downShift.Add(new ShiftPolygon.ShiftPolygonEntry(fullLoadCurve.MaxDragTorque * 1.1, p2.X.SI<PerSecond>()));
					if (downShiftPoints.Count == 0) {
						// coarse grid points in FLD
						downShift.Add(
							new ShiftPolygon.ShiftPolygonEntry(
								fullLoadCurve.FullLoadStationaryTorque(p2.X.SI<PerSecond>()) * ShiftPolygonEngineFldMargin,
								p2.X.SI<PerSecond>()));
						downShift.Add(
							new ShiftPolygon.ShiftPolygonEntry(
								fullLoadCurve.FullLoadStationaryTorque(p3.X.SI<PerSecond>()) * ShiftPolygonEngineFldMargin,
								p3.X.SI<PerSecond>()));
					} else {
						if (downShiftPoints.Min(x => x.X) > p2.X) {
							downShift.Add(
								new ShiftPolygon.ShiftPolygonEntry(
									fullLoadCurve.FullLoadStationaryTorque(p2.X.SI<PerSecond>()) * ShiftPolygonEngineFldMargin,
									p2.X.SI<PerSecond>()));
						}

						downShift.AddRange(
							downShiftPoints.Select(
								x => new ShiftPolygon.ShiftPolygonEntry(
									x.Y.SI<NewtonMeter>() * ShiftPolygonEngineFldMargin, x.X.SI<PerSecond>())));
						if (downShiftPoints.Max(x => x.X) < p3.X) {
							downShift.Add(
								new ShiftPolygon.ShiftPolygonEntry(
									fullLoadCurve.FullLoadStationaryTorque(p3.X.SI<PerSecond>()) * ShiftPolygonEngineFldMargin,
									p3.X.SI<PerSecond>()));
						}
					}
					downShift.Add(new ShiftPolygon.ShiftPolygonEntry(fullLoadCurve.MaxTorque * 1.1, p3.X.SI<PerSecond>()));
				}
				var upShift = new List<ShiftPolygon.ShiftPolygonEntry>();
				if (gearIdx >= gears.Count - 1) {
					return new ShiftPolygon(downShift, upShift);
				}

				upShift.Add(new ShiftPolygon.ShiftPolygonEntry(fullLoadCurve.MaxDragTorque * 1.1, p5.X.SI<PerSecond>()));
				upShift.Add(new ShiftPolygon.ShiftPolygonEntry(p5.Y.SI<NewtonMeter>(), p5.X.SI<PerSecond>()));
				return new ShiftPolygon(downShift, upShift);
			}

			public static ShiftPolygon ComputeManualTransmissionShiftPolygon(
				int gearIdx, EngineFullLoadCurve fullLoadCurve,
				IList<ITransmissionInputData> gears, CombustionEngineData engine, double axlegearRatio, Meter dynamicTyreRadius)
			{
				if (gears.Count < 2)
				{
					throw new VectoException("ComputeShiftPolygon needs at least 2 gears. {0} gears given.", gears.Count);
				}

				// ReSharper disable once InconsistentNaming
				var engineSpeed85kmhLastGear = ComputeEngineSpeed85kmh(gears[gears.Count - 1], axlegearRatio, dynamicTyreRadius);

				var nVHigh = VectoMath.Min(engineSpeed85kmhLastGear, engine.FullLoadCurves[0].RatedSpeed);

				var diffRatio = gears[gears.Count - 2].Ratio / gears[gears.Count - 1].Ratio - 1;

				var p1 = new Point(engine.IdleSpeed.Value() / 2, 0);
				var p2 = new Point(engine.IdleSpeed.Value() * 1.1, 0);
				var p3 = new Point(
					nVHigh.Value() * 0.9,
					fullLoadCurve.FullLoadStationaryTorque(nVHigh * 0.9).Value());

				var p4 = new Point((nVHigh * (1 + diffRatio / 3)).Value(), 0);
				var p5 = new Point(fullLoadCurve.N95hSpeed.Value(), fullLoadCurve.MaxTorque.Value());

				var p6 = new Point(p2.X, VectoMath.Interpolate(p1, p3, p2.X));
				var p7 = new Point(p4.X, VectoMath.Interpolate(p2, p5, p4.X));
				
				return ComputeManualTransmissionShiftPolygonBase(gearIdx, fullLoadCurve, gears, p2, p3, p4, p5, p6, p7);
			}

			public static ShiftPolygon ComputeManualTransmissionShiftPolygonExtended(
				int gearIdx,
				EngineFullLoadCurve fullLoadCurve,
				IList<ITransmissionInputData> gears,
				CombustionEngineData engine,
				double axlegearRatio,
				Meter dynamicTyreRadius)
			{
				if (gears.Count < 2)
				{
					throw new VectoException("ComputeShiftPolygon needs at least 2 gears. {0} gears given.", gears.Count);
				}

				// ReSharper disable once InconsistentNaming
				var engineSpeed85kmhLastGear = ComputeEngineSpeed85kmh(gears[gears.Count - 1], axlegearRatio, dynamicTyreRadius);
				var nVHigh = VectoMath.Min(engineSpeed85kmhLastGear, engine.FullLoadCurves[0].RatedSpeed);
				var diffRatio = gears[gears.Count - 2].Ratio / gears[gears.Count - 1].Ratio - 1;

				var p1 = new Point(engine.IdleSpeed.Value() / 2, 0);
				var p2 = new Point(engine.IdleSpeed.Value() * 1.1, 0);

				var p3 = new Point(
					nVHigh.Value() * 0.9,
					fullLoadCurve.FullLoadStationaryTorque(nVHigh * 0.9).Value());

				var p4 = new Point((nVHigh * (1 + diffRatio / 3)).Value(), 0);
				var p5 = new Point(fullLoadCurve.N95hSpeed.Value(), fullLoadCurve.MaxTorque.Value());

				var p6 = new Point(p2.X, VectoMath.Interpolate(p1, p3, p2.X));
				var p7 = new Point(p4.X, VectoMath.Interpolate(p2, p5, p4.X));

				/// Increase the torque at P6 by 20% and create a new extended shift polygon.
				var extendedRatio = 0.20;
				var p6YOffset = extendedRatio * p6.Y;
				var p3Extended = new Point(p3.X, p3.Y + p6YOffset);
				var p6Extended = new Point(p6.X, p6.Y + p6YOffset);

				return ComputeManualTransmissionShiftPolygonBase(gearIdx, fullLoadCurve, gears, p2, p3Extended, p4, p5, p6Extended, p7);
			}

			private static ShiftPolygon ComputeManualTransmissionShiftPolygonBase(
				int gearIdx,
				EngineFullLoadCurve fullLoadCurve,
				IList<ITransmissionInputData> gears,
				Point p2, Point p3, Point p4, Point p5, Point p6, Point p7)
			{
				var maxDragTorque = fullLoadCurve.MaxDragTorque * 1.1;
				var fldMargin = ShiftPolygonFldMargin(fullLoadCurve.FullLoadEntries, (p3.X * 0.95).SI<PerSecond>());
				var downshiftCorr = MoveDownshiftBelowFld(Edge.Create(p6, p3), fldMargin, 1.1 * fullLoadCurve.MaxTorque);

				var downShift = new List<ShiftPolygon.ShiftPolygonEntry>();
				if (gearIdx > 0)
				{
					downShift =
						new[] { p2, downshiftCorr.P1, downshiftCorr.P2 }.Select(
																			point => new ShiftPolygon.ShiftPolygonEntry(point.Y.SI<NewtonMeter>(), point.X.SI<PerSecond>()))
																		.ToList();

					downShift[0].Torque = maxDragTorque;
				}
				var upShift = new List<ShiftPolygon.ShiftPolygonEntry>();
				if (gearIdx >= gears.Count - 1)
				{
					return new ShiftPolygon(downShift, upShift);
				}

				var gearRatio = gears[gearIdx].Ratio / gears[gearIdx + 1].Ratio;
				var rpmMarginFactor = 1 + ShiftPolygonRPMMargin / 100.0;

				// ReSharper disable InconsistentNaming
				var p2p = new Point(p2.X * gearRatio * rpmMarginFactor, p2.Y / gearRatio);
				var p3p = new Point(p3.X * gearRatio * rpmMarginFactor, p3.Y / gearRatio);
				var p6p = new Point(p6.X * gearRatio * rpmMarginFactor, p6.Y / gearRatio);
				var edgeP6pP3p = new Edge(p6p, p3p);
				var p3pExt = new Point((1.1 * p5.Y - edgeP6pP3p.OffsetXY) / edgeP6pP3p.SlopeXY, 1.1 * p5.Y);

				// ReSharper restore InconsistentNaming

				var upShiftPts = IntersectTakeHigherShiftLine(new[] { p4, p7, p5 }, new[] { p2p, p6p, p3pExt });
				if (gears[gearIdx].MaxInputSpeed != null)
				{
					var maxSpeed = gears[gearIdx].MaxInputSpeed.Value();
					upShiftPts = IntersectTakeLowerShiftLine(
						upShiftPts,
						new[] { new Point(maxSpeed, 0), new Point(maxSpeed, upShiftPts.Max(pt => pt.Y)) });
				}
				upShift =
					upShiftPts.Select(point => new ShiftPolygon.ShiftPolygonEntry(point.Y.SI<NewtonMeter>(), point.X.SI<PerSecond>()))
							.ToList();
				upShift[0].Torque = maxDragTorque;

				return new ShiftPolygon(downShift, upShift);
			}

			/// <summary>
			/// ensures the original downshift line is below the (already reduced) full-load curve
			/// </summary>
			/// <param name="shiftLine">second part of the shift polygon (slope)</param>
			/// <param name="fldMargin">reduced full-load curve</param>
			/// <param name="maxTorque">max torque</param>
			/// <returns>returns a corrected shift polygon segment (slope) that is below the full load curve and reaches given maxTorque. the returned segment has the same slope</returns>
			internal static Edge MoveDownshiftBelowFld(Edge shiftLine, IEnumerable<Point> fldMargin, NewtonMeter maxTorque)
			{
				var slope = shiftLine.SlopeXY;
				var d = shiftLine.P2.Y - slope * shiftLine.P2.X;

				d = fldMargin.Select(point => point.Y - slope * point.X).Concat(new[] { d }).Min();
				var p6Corr = new Point(shiftLine.P1.X, shiftLine.P1.X * slope + d);
				var p3Corr = new Point((maxTorque.Value() - d) / slope, maxTorque.Value());
				return Edge.Create(p6Corr, p3Corr);
			}

			/// <summary>
			/// reduce the torque of the full load curve up to the given rpms
			/// </summary>
			/// <param name="fullLoadCurve"></param>
			/// <param name="rpmLimit"></param>
			/// <returns></returns>
			internal static IEnumerable<Point> ShiftPolygonFldMargin(
				List<EngineFullLoadCurve.FullLoadCurveEntry> fullLoadCurve,
				PerSecond rpmLimit)
			{
				return fullLoadCurve.TakeWhile(fldEntry => fldEntry.EngineSpeed < rpmLimit)
									.Select(
										fldEntry =>
											new Point(fldEntry.EngineSpeed.Value(), fldEntry.TorqueFullLoad.Value() * ShiftPolygonEngineFldMargin))
									.ToList();
			}

			// ReSharper disable once InconsistentNaming
			private static PerSecond ComputeEngineSpeed85kmh(
				ITransmissionInputData gear, double axleRatio,
				Meter dynamicTyreRadius)
			{
				var engineSpeed = TruckMaxAllowedSpeed / dynamicTyreRadius * axleRatio * gear.Ratio;
				return engineSpeed;
			}

			internal static Point[] IntersectTakeHigherShiftLine(Point[] orig, Point[] transformedDownshift)
			{
				var intersections = Intersect(orig, transformedDownshift);

				// add all points (i.e. intersecting points and both line segments) to a single list
				var pointSet = new List<Point>(orig);
				pointSet.AddRange(transformedDownshift);
				pointSet.AddRange(intersections);
				pointSet.AddRange(ProjectPointsToLineSegments(orig, transformedDownshift));
				pointSet.AddRange(ProjectPointsToLineSegments(transformedDownshift, orig));

				// line sweeping from max_X to 0: select point with lowest Y coordinate, abort if a point has Y = 0
				var shiftPolygon = new List<Point>();
				foreach (var xCoord in pointSet.Select(pt => pt.X).Distinct().OrderBy(x => x).Reverse()) {
					var coord = xCoord;
					var xPoints = pointSet.Where(pt => pt.X.IsEqual(coord) && !pt.Y.IsEqual(0)).ToList();
					shiftPolygon.Add(xPoints.MinBy(pt => pt.Y));
					var tmp = pointSet.Where(pt => pt.X.IsEqual(coord)).Where(pt => pt.Y.IsEqual(0)).ToList();
					if (!tmp.Any()) {
						continue;
					}

					shiftPolygon.Add(tmp.First());
					break;
				}

				// find and remove colinear points
				var toRemove = new List<Point>();
				for (var i = 0; i < shiftPolygon.Count - 2; i++) {
					var edge = new Edge(shiftPolygon[i], shiftPolygon[i + 2]);
					if (edge.ContainsXY(shiftPolygon[i + 1])) {
						toRemove.Add(shiftPolygon[i + 1]);
					}
				}
				foreach (var point in toRemove) {
					shiftPolygon.Remove(point);
				}

				// order points first by x coordinate and the by Y coordinate ASC
				return shiftPolygon.OrderBy(pt => pt.X).ThenBy(pt => pt.Y).ToArray();
			}

			internal static Point[] IntersectTakeLowerShiftLine(Point[] upShiftPts, Point[] upperLimit)
			{
				var intersections = Intersect(upShiftPts, upperLimit);
				if (!intersections.Any()) {
					return upShiftPts[0].X < upperLimit[0].X ? upShiftPts : upperLimit;
				}

				var pointSet = new List<Point>(upShiftPts);
				pointSet.AddRange(upperLimit);
				pointSet.AddRange(intersections);
				pointSet.AddRange(ProjectPointsToLineSegments(upShiftPts, upperLimit, true));
				pointSet.AddRange(ProjectPointsToLineSegments(upperLimit, upShiftPts, true));

				var shiftPolygon = new List<Point>();
				foreach (var yCoord in pointSet.Select(pt => pt.Y).Distinct().OrderBy(y => y).Reverse()) {
					var yPoints = pointSet.Where(pt => pt.Y.IsEqual(yCoord)).ToList();
					shiftPolygon.Add(yPoints.MinBy(pt => pt.X));
				}

				// find and remove colinear points
				var toRemove = new List<Point>();
				for (var i = 0; i < shiftPolygon.Count - 2; i++) {
					var edge = new Edge(shiftPolygon[i], shiftPolygon[i + 2]);
					if (edge.ContainsXY(shiftPolygon[i + 1])) {
						toRemove.Add(shiftPolygon[i + 1]);
					}
				}
				foreach (var point in toRemove) {
					shiftPolygon.Remove(point);
				}

				// order points first by x coordinate and the by Y coordinate ASC
				return shiftPolygon.OrderBy(pt => pt.X).ThenBy(pt => pt.Y).ToArray();
			}

			private static Point[] Intersect(Point[] orig, Point[] transformedDownshift)
			{
				var intersections = new List<Point>();

				// compute all intersection points between both line segments
				// ReSharper disable once LoopCanBeConvertedToQuery
				foreach (var origLine in orig.Pairwise(Edge.Create)) {
					// ReSharper disable once LoopCanBeConvertedToQuery
					foreach (var transformedLine in transformedDownshift.Pairwise(Edge.Create)) {
						var isect = VectoMath.Intersect(origLine, transformedLine);
						if (isect != null) {
							intersections.Add(isect);
						}
					}
				}

				return intersections.ToArray();
			}

			private static IEnumerable<Point> ProjectPointsToLineSegments(
				IEnumerable<Point> lineSegments, Point[] points,
				bool projectToVertical = false)
			{
				var pointSet = new List<Point>();
				foreach (var segment in lineSegments.Pairwise(Edge.Create)) {
					if (segment.P1.X.IsEqual(segment.P2.X)) {
						if (projectToVertical) {
							pointSet.AddRange(
								points.Select(point => new Point(segment.P1.X, point.Y))
									.Where(pt => pt.Y.IsBetween(segment.P1.Y, segment.P2.Y)));
						}
						continue;
					}

					var k = segment.SlopeXY;
					var d = segment.P1.Y - segment.P1.X * k;
					pointSet.AddRange(points.Select(point => new Point(point.X, point.X * k + d)));
				}

				return pointSet;
			}
		}

		public static class TorqueConverter
		{
			public static readonly PerSecond ReferenceRPM = 1000.RPMtoRad();
			public static readonly PerSecond MaxInputSpeed = 5000.RPMtoRad();
			public static readonly MeterPerSquareSecond CLUpshiftMinAcceleration = 0.1.SI<MeterPerSquareSecond>();
			public static readonly MeterPerSquareSecond CCUpshiftMinAcceleration = 0.1.SI<MeterPerSquareSecond>();

			private static readonly PerSecond DownshiftPRM = 700.RPMtoRad();
			private static readonly PerSecond UpshiftLowRPM = 900.RPMtoRad();
			private static readonly PerSecond UpshiftHighRPM = 1150.RPMtoRad();

			public static ShiftPolygon ComputeShiftPolygon(
				EngineFullLoadCurve fullLoadCurve, bool first = false,
				bool last = false)
			{
				var maxDragTorque = fullLoadCurve.MaxDragTorque * 1.1;
				var maxTorque = fullLoadCurve.MaxTorque * 1.1;
				var p0 = new Point(UpshiftLowRPM.Value(), maxDragTorque.Value());
				var p1 = new Point(UpshiftLowRPM.Value(), 0);
				var p2 = new Point(UpshiftHighRPM.Value(), fullLoadCurve.FullLoadStationaryTorque(UpshiftHighRPM).Value());
				var edge = new Edge(p1, p2);
				var p2corr = new Point((maxTorque.Value() - edge.OffsetXY) / edge.SlopeXY, maxTorque.Value());

				var downshift = new[] {
					new ShiftPolygon.ShiftPolygonEntry(maxDragTorque, DownshiftPRM),
					new ShiftPolygon.ShiftPolygonEntry(maxTorque, DownshiftPRM)
				};
				var upshift = new[] { p0, p1, p2corr }.Select(
					pt => new ShiftPolygon.ShiftPolygonEntry(pt.Y.SI<NewtonMeter>(), pt.X.SI<PerSecond>()));

				return new ShiftPolygon(
					first ? new List<ShiftPolygon.ShiftPolygonEntry>() : downshift.ToList(),
					last ? new List<ShiftPolygon.ShiftPolygonEntry>() : upshift.ToList());
			}

			public static IEnumerable<TorqueConverterEntry> GetTorqueConverterDragCurve(double ratio, TorqueConverterEntry first, TorqueConverterEntry last)
			{
				var characteristicTorque = new[] {
					new TorqueConverterEntry() {
						SpeedRatio = 1,
						TorqueRatio = last.TorqueRatio * 0.99,
						Torque = 0.SI<NewtonMeter>()
					},
					new TorqueConverterEntry(
					) {
						SpeedRatio = 5,
						TorqueRatio = 0.9,
						Torque =  -4 * first.Torque
					},
					new TorqueConverterEntry() {
						SpeedRatio = 15,
						TorqueRatio = 0.85,
						Torque =  -4.1 * first.Torque
					},
				};
				foreach (var torqueConverterEntry in characteristicTorque) {
					torqueConverterEntry.SpeedRatio = torqueConverterEntry.SpeedRatio * ratio;
					torqueConverterEntry.TorqueRatio = torqueConverterEntry.TorqueRatio / ratio;
				}

				return characteristicTorque.Where(x => x.SpeedRatio >= ratio).ToArray();
			}
		}

		public static class PTO
		{
			public const string DefaultPTOTechnology =
				"only the drive shaft of the PTO - shift claw, synchronizer, sliding gearwheel";

			public const string DefaultPTOIdleLosses =
				DeclarationDataResourcePrefix + ".MissionCycles.MunicipalUtility_PTO_generic.vptol";

			public const string DefaultPTOActivationCycle =
				DeclarationDataResourcePrefix + ".MissionCycles.MunicipalUtility_PTO_generic.vptoc";

			public const string DefaultE_PTOActivationCycle = DeclarationDataResourcePrefix + ".MissionCycles.MunicipalUtility_PTO_generic.vptoel";
		}

		public static class VTPMode
		{
			public static readonly Meter RunInThreshold = 15000.SI(Unit.SI.Kilo.Meter).Cast<Meter>();
			public const double EvolutionCoefficient = 0.98;

			public const MissionType SelectedMissionMediumLorry = MissionType.RegionalDelivery;

			public const MissionType SelectedMissionLowFloorBus = MissionType.Urban;
			public const MissionType SelectedMissionHighFloorBus = MissionType.Coach;

			public const LoadingType SelectedLoading = LoadingType.ReferenceLoad;

			public static MissionType GetSelectedMissionHeavyLorry(VehicleClass vc)
			{
				return vc.IsOneOf(VehicleClass.Class1, VehicleClass.Class2, VehicleClass.Class3)
					? MissionType.RegionalDelivery
					: MissionType.LongHaul;
			}

			// verification of input data

			public const double WheelSpeedDifferenceFactor = 1.4;
			public const double WheelTorqueDifferenceFactor = 3;

			public static readonly PerSecond WheelSpeedZeroTolerance = 0.1.RPMtoRad();
			public static readonly PerSecond MaxWheelSpeedDifferenceStandstill = 1.RPMtoRad();

			public static readonly PerSecond MinFanSpeed = 20.RPMtoRad();
			public static readonly PerSecond MaxFanSpeed = 4000.RPMtoRad();

			public static readonly Second SamplingInterval = 0.5.SI<Second>();

			public static readonly WattSecond MinPosWorkAtWheelsForFC = 1.SI(Unit.SI.Kilo.Watt.Hour).Cast<WattSecond>();

			public static readonly SpecificFuelConsumption LowerFCThreshold =
				180.SI(Unit.SI.Gramm.Per.Kilo.Watt.Hour).Cast<SpecificFuelConsumption>();

			public static readonly SpecificFuelConsumption UpperFCThreshold =
				600.SI(Unit.SI.Gramm.Per.Kilo.Watt.Hour).Cast<SpecificFuelConsumption>();

			public static readonly Second FCAccumulationWindow = 10.SI(Unit.SI.Minute).Cast<Second>();
			public static readonly double[] FanParameters = { 7.320, 1200.0, 810 };
		}

		public static class Vehicle
		{
			public const bool DualFuelVehicleDefault = false;
			public const bool HybridElectricHDVDefault = false;
			public const bool ZeroEmissionVehicleDefault = false;
			public const TankSystem TankSystemDefault = TankSystem.Compressed;
			public const bool SleeperCabDefault = true;
			public const bool VocationalVehicleDefault = false;

			public static class ADAS
			{
				public const PredictiveCruiseControlType PredictiveCruiseControlDefault = PredictiveCruiseControlType.None;
				public const EcoRollType EcoRoll = EcoRollType.None;
				public const bool EngineStopStartDefault = false;
			}
		}

		public static class SuperCap
		{
			public const double SocMin = 0.45;
		}


		public static class Battery
		{
			public static GenericSOC GenericSOC = new GenericSOC();

			/// <summary>
			/// Percentage of the maximum voltage of the battery
			/// </summary>
			private const double SOCMinHP = 0.05;
			private const double SOCMaxHP = 0.95;

			private const double SOCMinHE = 0.05;
			private const double SOCMaxHE = 0.95;
			
			public static readonly Ohm CablesAndConnectorsResistance = 0.63.SI(Unit.SI.Milli.Ohm).Cast<Ohm>();
			public static readonly Ohm JunctionBoxResistance = 1.3.SI(Unit.SI.Milli.Ohm).Cast<Ohm>();

			public static double GetMinSoc(BatteryType type)
			{
				switch (type) {
					case BatteryType.HPBS:
						return SOCMinHP;
					case BatteryType.HEBS:
						return SOCMinHE;
					default:
						throw new ArgumentOutOfRangeException(nameof(type), type, null);
				}
			}

			public const double GenericDeterioration = 0.05;

			public static double GetMaxSoc(BatteryType type)
			{
				switch (type)
				{
					case BatteryType.HPBS:
						return SOCMaxHP;
					case BatteryType.HEBS:
						return SOCMaxHE;
					default:
						throw new ArgumentOutOfRangeException(nameof(type), type, null);
				}
			}
		}

		public static int GetDeclarationReportFinalResultEntryIndex<T>(List<T> results, VectoSimulationJobType jobType) where T:IResultEntry
		{
			if (results.Any(r => r.OVCMode == OvcHevMode.ChargeSustaining))
			{
				/// Non-OVC FCHV pre-runs should not be taken into account for the final result.
				/// FCHVs Iteration == 0 -> PEV pre-run.
				/// For OVC FCHV ChargeDepleting (CD) Iteration == 0 entries are required to calculate CD consumptions.
				return results
					.Select((r, idx) => (entry: r, index: idx))
					.Where(r => jobType.IsFCHV() ? r.entry.OVCIteration != 0 || r.entry.OVCMode == OvcHevMode.ChargeDepleting : true)
					.MinBy(r => Math.Abs(r.entry.DeltaSoC)).index;
			}

			return results.Count - 1;
		}

		public static int GetSumDataFinalResultEntryIndex(List<DataRow> results)
		{
			if (results.Any(r => r.Field<string>(SumDataFields.OVCHEVMode) == OvcHevMode.ChargeSustaining.ToString())) {
				return results
					.Select((r, idx) =>
						Tuple.Create(
							Math.Abs(r.Field<double>(SumDataFields.REESS_EndSoC) -
									r.Field<double>(SumDataFields.REESS_StartSoC)), idx)).MinBy(x => x.Item1).Item2;
			}

			return results.Count - 1;
		}

        public static IWeightedResult CalculateWeightedResult(IResultEntry cdResult, IResultEntry csResult)
		{
			var vehicleOperation = VehicleOperation.LookupVehicleOperation(cdResult.VehicleClass, cdResult.Mission);
			//CalculateChargingEfficiencyOVCHEV(cdResult.MaxChargingPower, vehicleOperation, cdResult.BatteryData);

			if (cdResult.VectoRunData.InMotionCharging) {
				//var chgEfficiencies = CalculateChargingEfficiencyIMCOVCHEV(cdResult.VectoRunData, vehicleOperation);
				return CalculateWeightedResultIMC(cdResult, csResult, vehicleOperation);
			}
			var chgEfficiency = CalculateChargingEfficiencyOVCHEV(cdResult.VectoRunData, vehicleOperation);
			return CalculateWeightedResult(cdResult, csResult, vehicleOperation, chgEfficiency);
		}

		public static IWeightedResult CalculateWeightedResultCompletedBus(IResultEntry cdResult, IResultEntry csResult)
		{
			var vehicleOperation = VehicleOperation.LookupVehicleOperation(cdResult.VehicleClass, cdResult.Mission);
			var chargingEff = new ChargingEfficiencies() {
				EtaChargingWeighted = 1,
				EtaChargingInMission = 1,
				EtaChargingInMotion = 1,
				EtaChargingDepot = 1
			};
			return CalculateWeightedResult(cdResult, csResult, vehicleOperation, chargingEff);
		}

		private static IWeightedResult CalculateWeightedResultIMC(IResultEntry cdResult,
			IResultEntry csResult,
			VehicleOperationLookup.VehicleOperationData vehicleOperation)
		{
			if (cdResult.Status != VectoRun.Status.Success || csResult.Status != VectoRun.Status.Success) {
				return null;
			}
			var batteryData = cdResult.BatteryData;
			if (batteryData == null) {
				throw new VectoException("Battery Data is required for OVC post-processing");
			}

			var D19_dailySpecificMileage = vehicleOperation.Mileage.DailyMileage;
			//var D20_stationarychargingDuringMissionMaxPwrInfastructure = vehicleOperation.StationaryChargingMaxPwrInfrastructure;
			//var D21_stationaryChargingDuringMission_AvgDurationPerEvent = vehicleOperation.StationaryChargingDuringMission_AvgDurationPerEvent;
			//var D22_stationaryChargingDuringMission_NbrEvents = vehicleOperation.StationaryChargingDuringMission_NbrEvents;
			var D23_realWorldFactorUsageStartSoC = vehicleOperation.RealWorldUsageFactors.StartSoCBeforeMission;
			//var D24_realWorldFactorChargeDuringMission = 0.0; // vehicleOperation.RealWorldUsageFactors.StationaryChargingDuringMission;
			var D25_shareOfDistanceWithInMotionCharging = GetShareIMCInfrastructure(cdResult.VectoRunData.InMotionChargingTechnology, vehicleOperation);
			var D26_realWorldFactorInMotionChargingDuringMission = vehicleOperation.RealWorldUsageFactors.InMotionChargingDuringMission;

			//var D9_maxStatChargingPower = cdResult.MaxChargingPower;
			var D10_useableBatteryCapForR_CDA = cdResult.BatteryData.UseableStoredEnergy;

			var D11_energyConsumptionCdMode = cdResult.ElectricEnergyConsumption / cdResult.Distance;
			var D12_fuelConsumptionCdMode = cdResult.FuelData.Sum(x =>
				cdResult.FuelConsumptionFinal(x.FuelType).TotalFuelConsumptionCorrected * x.LowerHeatingValueVecto);
			var D13_fuelConsumptionCsMode = csResult.FuelData.Sum(x =>
				csResult.FuelConsumptionFinal(x.FuelType).TotalFuelConsumptionCorrected * x.LowerHeatingValueVecto);

			var D15_actualChargeDepletingRange = D10_useableBatteryCapForR_CDA / D11_energyConsumptionCdMode;
			var D16_equivalentAllElectricRange = D15_actualChargeDepletingRange *
												((D13_fuelConsumptionCsMode - D12_fuelConsumptionCdMode) /
												D13_fuelConsumptionCsMode);
			var D17_zeroCO2EmissionsRange = D16_equivalentAllElectricRange;

			var D28_elRangefromStartSoC_ChargingAtDepot = D15_actualChargeDepletingRange * D23_realWorldFactorUsageStartSoC;
			var D29_electricEnergyFromStartSoC = D11_energyConsumptionCdMode * D28_elRangefromStartSoC_ChargingAtDepot;
			//var D30_chargingEfficiencyBatteryStationaryDuringMission = 0; // not relevant 
			  // double.NaN;
			  //VectoMath.Min(
			  //    VectoMath.Min(D9_maxStatChargingPower, D20_stationarychargingDuringMissionMaxPwrInfastructure) *
			  //    D21_stationaryChargingDuringMission_AvgDurationPerEvent * D29_chargingEffBattInMission,
			  //    D10_useableBatteryCapForR_CDA) * D22_stationaryChargingDuringMission_NbrEvents * D24_realWorldFactorChargeDuringMission;
			var D31_electricEnergyChargedDuringMissionFromStatInfrastructure = 0.SI<WattSecond>(); // always 0 becauseD24_realWorldFactorChargeDuringMission is 0
				//       VectoMath.Min(
					//	VectoMath.Min(D9_maxStatChargingPower, D20_stationarychargingDuringMissionMaxPwrInfastructure) *
					//				D21_stationaryChargingDuringMission_AvgDurationPerEvent *
					//				D30_chargingEfficiencyBatteryStationaryDuringMission, D10_useableBatteryCapForR_CDA) *
					//D22_stationaryChargingDuringMission_NbrEvents * D24_realWorldFactorChargeDuringMission;

			var D32_electridRageforUFFromStatChgDuringMission =
				D31_electricEnergyChargedDuringMissionFromStatInfrastructure / D11_energyConsumptionCdMode;
			var D33_electricRangeForUFFromInMotionCharging = D19_dailySpecificMileage * D25_shareOfDistanceWithInMotionCharging;
			var D34_electricEnergyDirectFeed = D11_energyConsumptionCdMode * D33_electricRangeForUFFromInMotionCharging;
			var D35_electricEnergyChargedDuringMissionInMotion = D10_useableBatteryCapForR_CDA * D26_realWorldFactorInMotionChargingDuringMission;
			var D36_electridRangeForUFFromInMotionCharging = D35_electricEnergyChargedDuringMissionInMotion / D11_energyConsumptionCdMode;

			var D38_utilityFactor = VectoMath.Min(1.0,
				(D28_elRangefromStartSoC_ChargingAtDepot + D32_electridRageforUFFromStatChgDuringMission +
				D33_electricRangeForUFFromInMotionCharging + D36_electridRangeForUFFromInMotionCharging) /
				D19_dailySpecificMileage);

			var D40_electricEnergyReqForDailyMileage = D11_energyConsumptionCdMode * D19_dailySpecificMileage;
			var D41_limitationElectricEnergyChargedIntoBattery = VectoMath.Max(0.0,
				D40_electricEnergyReqForDailyMileage - D34_electricEnergyDirectFeed);

			var D43_shareElectricEnergyFromGridFirstCharged = D41_limitationElectricEnergyChargedIntoBattery /
															D40_electricEnergyReqForDailyMileage;

			var chargingEfficiency = CalculateChargingEfficiencyIMCOVCHEV(cdResult.VectoRunData, vehicleOperation,
				D29_electricEnergyFromStartSoC, D31_electricEnergyChargedDuringMissionFromStatInfrastructure,
				D35_electricEnergyChargedDuringMissionInMotion);

			var D44_averageChargingEfficiencyDuringExtCharging = chargingEfficiency.EtaChargingWeighted;
			var D45_shareElectricEnergyFromGrid = 1 - D43_shareElectricEnergyFromGridFirstCharged;
			var D46_averageDischargeEfficiencyBattery = cdResult.BatteryEfficiencyDischarge;

			var D48_correctionFactor_ECSoC_to_ECTerminal =
				D43_shareElectricEnergyFromGridFirstCharged * (1 / D44_averageChargingEfficiencyDuringExtCharging) +
				D45_shareElectricEnergyFromGrid * D46_averageDischargeEfficiencyBattery;

			var D50_electricEnergyConsumptionWeighted =
				D11_energyConsumptionCdMode * D48_correctionFactor_ECSoC_to_ECTerminal;

			var D52_electricEnergyConsumptionWeighted = D38_utilityFactor * D50_electricEnergyConsumptionWeighted;
			var D53_fuelConsumptionWeighted = cdResult.FuelData.Select(x => Tuple.Create(x,
					D38_utilityFactor * cdResult.FuelConsumptionFinal(x.FuelType).TotalFuelConsumptionCorrected +
					(1 - D38_utilityFactor) * csResult.FuelConsumptionFinal(x.FuelType).TotalFuelConsumptionCorrected))
				.ToDictionary(x => x.Item1, x => x.Item2);

            var fcPerMeter = cdResult.FuelData.Select(fd => (fuelData: fd,
                    fcPerMeterWeighted: D38_utilityFactor * cdResult.FuelConsumptionFinal(fd.FuelType).TotalFuelConsumptionCorrected / cdResult.Distance +
                    (1 - D38_utilityFactor) * csResult.FuelConsumptionFinal(fd.FuelType).TotalFuelConsumptionCorrected / csResult.Distance))
                .ToDictionary(r => r.fuelData, r => r.fcPerMeterWeighted);

            var retVal = new WeightedResult() {
				Status = VectoRun.Status.Success,
				JobType = cdResult.VectoRunData.JobType,
				OffVehicleCharging = cdResult.VectoRunData.VehicleData.OffVehicleCharging,
				Distance = cdResult.Distance,
				Payload = cdResult.Payload,
				CargoVolume = cdResult.CargoVolume,
				PassengerCount = cdResult.PassengerCount,
				AverageSpeed = cdResult.AverageSpeed,
				AverageDrivingSpeed = cdResult.AverageDrivingSpeed,
				ActualChargeDepletingRange = D15_actualChargeDepletingRange,
				EquivalentAllElectricRange = D16_equivalentAllElectricRange,
				ZeroCO2EmissionsRange = D17_zeroCO2EmissionsRange,
				HydrogenRange = D17_zeroCO2EmissionsRange,
				UtilityFactor = D38_utilityFactor,
				ElectricEnergyConsumption = D52_electricEnergyConsumptionWeighted * cdResult.Distance,
				FuelConsumption = D53_fuelConsumptionWeighted,
				CO2PerMeter = (D38_utilityFactor * (cdResult.CO2Total / cdResult.Distance)) + ((1 - D38_utilityFactor) * (csResult.CO2Total / csResult.Distance)),
				FuelConsumptionPerMeter = fcPerMeter,
				BeginOfLifeRanges = cdResult.BeginOfLifeRanges,
				EndOfLifeRanges = cdResult.EndOfLifeRanges,
				
				AuxHeaterFuel = cdResult.AuxHeaterFuel,
				ZEV_CO2 =
					cdResult.AuxHeaterFuel != null && cdResult.ZEV_CO2 != null &&
					csResult.ZEV_FuelConsumption_AuxHtr != null
						? (D38_utilityFactor * (cdResult.ZEV_CO2 / cdResult.Distance)) + ((1 - D38_utilityFactor) * (csResult.ZEV_CO2 / csResult.Distance))
						: null,
				ZEV_FuelConsumption_AuxHtr =
					cdResult.AuxHeaterFuel != null && cdResult.ZEV_FuelConsumption_AuxHtr != null &&
					csResult.ZEV_FuelConsumption_AuxHtr != null
						? (D38_utilityFactor * (cdResult.ZEV_FuelConsumption_AuxHtr / cdResult.Distance)) +
						((1 - D38_utilityFactor) * (csResult.ZEV_FuelConsumption_AuxHtr / csResult.Distance))
						: null,
			};

			return retVal;
		}

		private static IWeightedResult CalculateWeightedResult(IResultEntry cdResult, 
																IResultEntry csResult, 
																VehicleOperationLookup.VehicleOperationData vehicleOperation,
																ChargingEfficiencies chargingEfficiency)
		{
			if (!cdResult.Status.IsOneOf(VectoRun.Status.Success, VectoRun.Status.PrimaryBusSimulationIgnore) || 
				!csResult.Status.IsOneOf(VectoRun.Status.Success, VectoRun.Status.PrimaryBusSimulationIgnore)) {
				return null;
			}
			var batteryData = cdResult.BatteryData;
			if (batteryData == null) {
				throw new VectoException("Battery Data is required for OVC post-processing");
			}

			var D19_dailySpecificMileage = vehicleOperation.Mileage.DailyMileage;
			var D20_stationarychargingDuringMissionMaxPwrInfastructure = vehicleOperation.StationaryChargingMaxPwrInfrastructure;
			var D21_stationaryChargingDuringMission_AvgDurationPerEvent = vehicleOperation.StationaryChargingDuringMission_AvgDurationPerEvent;
			var D22_stationaryChargingDuringMission_NbrEvents = vehicleOperation.StationaryChargingDuringMission_NbrEvents;
			var D23_realWorldFactorUsageStartSoC = vehicleOperation.RealWorldUsageFactors.StartSoCBeforeMission;
			var D24_realWorldFactorChargeDuringMission = vehicleOperation.RealWorldUsageFactors.StationaryChargingDuringMission;

			//var (etaChgBatDepot, etaChgBatInMission, etaChtBatWeighted) = chargingEfficiency;
			
			var D9_maxStatChargingPower = cdResult.MaxChargingPower;

			var D11_energyConsumptionCdMode = cdResult.ElectricEnergyConsumption / cdResult.Distance;
			var D12_fuelConsumptionCdMode = cdResult.FuelData.Sum(x =>
				cdResult.FuelConsumptionFinal(x.FuelType).TotalFuelConsumptionCorrected * x.LowerHeatingValueVecto);
			var D13_fuelConsumptionCsMode = csResult.FuelData.Sum(x =>
				csResult.FuelConsumptionFinal(x.FuelType).TotalFuelConsumptionCorrected * x.LowerHeatingValueVecto);

			var D10_useableBatteryCapForR_CDA = cdResult.BatteryData.UseableStoredEnergy;
			var D15_actualChargeDepletingRange = D10_useableBatteryCapForR_CDA / D11_energyConsumptionCdMode;
			var D16_equivalentAllElectricRange = D15_actualChargeDepletingRange *
												((D13_fuelConsumptionCsMode - D12_fuelConsumptionCdMode) /
												D13_fuelConsumptionCsMode);
			var D17_zeroCO2EmissionsRange = D16_equivalentAllElectricRange;

			var D27_elRangefromStartSoC_ChargingAtDepot = D15_actualChargeDepletingRange * D23_realWorldFactorUsageStartSoC;
			var D28_chargingEffBattInMission = chargingEfficiency.EtaChargingInMission;
			var D29_electricEnergyChargedDuringMissionStatInfrastructure =
				VectoMath.Min(
					VectoMath.Min(D9_maxStatChargingPower, D20_stationarychargingDuringMissionMaxPwrInfastructure) *
					D21_stationaryChargingDuringMission_AvgDurationPerEvent * D28_chargingEffBattInMission,
					D10_useableBatteryCapForR_CDA) * D22_stationaryChargingDuringMission_NbrEvents * D24_realWorldFactorChargeDuringMission;
			var D30_elRangeStatChargingDuringMission = D29_electricEnergyChargedDuringMissionStatInfrastructure / D11_energyConsumptionCdMode;

			var D32_utilityFactor = Math.Min(1, (D27_elRangefromStartSoC_ChargingAtDepot + D30_elRangeStatChargingDuringMission) / D19_dailySpecificMileage);

			var D25_chargingEffBattWeighted = chargingEfficiency.EtaChargingWeighted;
			var D34_electricEnergyCdModeTerminal = cdResult.ElectricEnergyConsumption / D25_chargingEffBattWeighted;

			var D36_electricEnergyConsumptionWeighted = D32_utilityFactor * D34_electricEnergyCdModeTerminal;
			var D37_fuelConsumptionWeighted = cdResult.FuelData.Select(x => Tuple.Create(x,
					D32_utilityFactor * cdResult.FuelConsumptionFinal(x.FuelType).TotalFuelConsumptionCorrected +
					(1 - D32_utilityFactor) * csResult.FuelConsumptionFinal(x.FuelType).TotalFuelConsumptionCorrected))
				.ToDictionary(x => x.Item1, x => x.Item2);

            var fcPerMeter = cdResult.FuelData.Select(fd => (fuelData: fd,
                    fcPerMeterWeighted: D32_utilityFactor * cdResult.FuelConsumptionFinal(fd.FuelType).TotalFuelConsumptionCorrected / cdResult.Distance +
                    (1 - D32_utilityFactor) * csResult.FuelConsumptionFinal(fd.FuelType).TotalFuelConsumptionCorrected / csResult.Distance))
                .ToDictionary(r => r.fuelData, r => r.fcPerMeterWeighted);

            var retVal = new WeightedResult() {
				Status = cdResult.Status == VectoRun.Status.PrimaryBusSimulationIgnore || csResult.Status == VectoRun.Status.PrimaryBusSimulationIgnore ? VectoRun.Status.PrimaryBusSimulationIgnore : VectoRun.Status.Success,
				JobType = cdResult.VectoRunData.JobType,
				OffVehicleCharging = cdResult.VectoRunData.VehicleData.OffVehicleCharging,
				Distance = cdResult.Distance,
				Payload = cdResult.Payload,
				CargoVolume = cdResult.CargoVolume,
				PassengerCount = cdResult.PassengerCount,
				AverageSpeed = cdResult.AverageSpeed,
				AverageDrivingSpeed = cdResult.AverageDrivingSpeed,
				ActualChargeDepletingRange = D15_actualChargeDepletingRange,
				EquivalentAllElectricRange = D16_equivalentAllElectricRange,
				ZeroCO2EmissionsRange = D17_zeroCO2EmissionsRange,
				HydrogenRange = D17_zeroCO2EmissionsRange,
				UtilityFactor = D32_utilityFactor,
				ElectricEnergyConsumption = D36_electricEnergyConsumptionWeighted,
				FuelConsumption = D37_fuelConsumptionWeighted,
				FuelConsumptionPerMeter = fcPerMeter,
				BeginOfLifeRanges = cdResult.BeginOfLifeRanges,
				EndOfLifeRanges = cdResult.EndOfLifeRanges,

                CO2PerMeter = (D32_utilityFactor * (cdResult.CO2Total / cdResult.Distance)) + ((1 - D32_utilityFactor) * (csResult.CO2Total / csResult.Distance)),

				AuxHeaterFuel = cdResult.AuxHeaterFuel,
				ZEV_CO2 =
					cdResult.AuxHeaterFuel != null && cdResult.ZEV_CO2 != null &&
					csResult.ZEV_FuelConsumption_AuxHtr != null
						? (D32_utilityFactor * (cdResult.ZEV_CO2 / cdResult.Distance)) + ((1 - D32_utilityFactor) * (csResult.ZEV_CO2 / csResult.Distance))
						: null,
				ZEV_FuelConsumption_AuxHtr =
					cdResult.AuxHeaterFuel != null && cdResult.ZEV_FuelConsumption_AuxHtr != null &&
					csResult.ZEV_FuelConsumption_AuxHtr != null
						? (D32_utilityFactor * (cdResult.ZEV_FuelConsumption_AuxHtr / cdResult.Distance)) +
						((1 - D32_utilityFactor) * (csResult.ZEV_FuelConsumption_AuxHtr / csResult.Distance))
						: null,
			};

			return retVal;
		}


		public static ChargingEfficiencies CalculateChargingEfficiencyOVCHEV(VectoRunData runData,
			VehicleOperationLookup.VehicleOperationData vehicleOperation)
		{
			var batteryData = runData.BatteryData;
			var depotChargingPower =
				VectoMath.Max(MinDepotChgPwr, batteryData.UseableStoredEnergy / DepotChargingDuration);

			var inMissionChargingPower = VectoMath.Min(
				vehicleOperation.StationaryChargingMaxPwrInfrastructure,
				runData.MaxChargingPower);

			var tmpBattery = new BatterySystem(null, batteryData);
			var centerSoC = (tmpBattery.MinSoC + tmpBattery.MaxSoC) / 2.0;
			tmpBattery.Initialize(centerSoC);

			var respChgBatDepot = tmpBattery.Request(0.SI<Second>(), 1.SI<Second>(), depotChargingPower, true);
			var respChgBatInMission = tmpBattery.Request(0.SI<Second>(), 1.SI<Second>(), inMissionChargingPower, true);

			var currentEstInMission = depotChargingPower / tmpBattery.InternalVoltage;
			var connectorLossInMission = currentEstInMission * batteryData.ConnectionSystemResistance *
								currentEstInMission;
			var currentEstDepot = depotChargingPower / tmpBattery.InternalVoltage;
			var connectorLossDepot = currentEstDepot * batteryData.ConnectionSystemResistance *
								currentEstDepot;

			var etaChgBatDepot = 1 - ((respChgBatDepot.LossPower + connectorLossDepot) / respChgBatDepot.PowerDemand).Value();
			var etaChgBatInMission = 1 - ((respChgBatInMission.LossPower + connectorLossInMission) / respChgBatInMission.PowerDemand).Value();


			var chargedEnergyDepot = batteryData.UseableStoredEnergy * vehicleOperation.RealWorldUsageFactors.StartSoCBeforeMission;
			var chargedEnergyPerEventInMission = inMissionChargingPower * vehicleOperation.StationaryChargingDuringMission_AvgDurationPerEvent *
												etaChgBatInMission;
			var chargedEnergyInMission = VectoMath.Min(chargedEnergyPerEventInMission, batteryData.UseableStoredEnergy) *
				vehicleOperation.StationaryChargingDuringMission_NbrEvents *
				vehicleOperation.RealWorldUsageFactors.StationaryChargingDuringMission;
			var totalChargedEnergy = chargedEnergyDepot + chargedEnergyInMission;

			//return (etaChgBatDepot, etaChgBatInMission, etaChgBatDepot * chargedEnergyDepot / totalChargedEnergy +
			//											etaChgBatInMission * chargedEnergyInMission /
			//											totalChargedEnergy);
			return new ChargingEfficiencies() {
				EtaChargingDepot = etaChgBatDepot,
				EtaChargingInMission = etaChgBatInMission,
				EtaChargingInMotion = double.NaN,
				EtaChargingWeighted = etaChgBatDepot * chargedEnergyDepot / totalChargedEnergy +
									etaChgBatInMission * chargedEnergyInMission /
									totalChargedEnergy
			};

		}

        public static double CalculateChargingEfficiencyPEV(VectoRunData runData)
		{
			var batteryData = runData.BatteryData;
			var tmpBattery = new BatterySystem(null, batteryData);
			var centerSoC = (tmpBattery.MinSoC + tmpBattery.MaxSoC) / 2.0;
			tmpBattery.Initialize(centerSoC);

			var depotChargingPower =
				VectoMath.Max(MinDepotChgPwr, batteryData.UseableStoredEnergy / DepotChargingDuration);

			var respChgBatDepot = tmpBattery.Request(0.SI<Second>(), 1.SI<Second>(), depotChargingPower, true);
			var currentEst = depotChargingPower / tmpBattery.InternalVoltage;
			var connectorLoss = currentEst * (runData.BatteryData?.ConnectionSystemResistance ?? 0.SI<Ohm>()) *
								currentEst;
			var etaChgBatDepot = 1 - ((respChgBatDepot.LossPower + connectorLoss ) / respChgBatDepot.PowerDemand).Value();
			return etaChgBatDepot;
		}

		public static double CalculateChargingEfficiencyIMCPEV(VectoRunData runData, WattSecond energyDepot, WattSecond energyInMotion)
		{
			var batteryData = runData.BatteryData;
			var tmpBattery = new BatterySystem(null, batteryData);
			var centerSoC = (tmpBattery.MinSoC + tmpBattery.MaxSoC) / 2.0;
			tmpBattery.Initialize(centerSoC);

			var depotChargingPower =
				VectoMath.Max(MinDepotChgPwr, batteryData.UseableStoredEnergy / DepotChargingDuration);
			var respChgBatDepot = tmpBattery.Request(0.SI<Second>(), 1.SI<Second>(), depotChargingPower, true);
			var currentEstDep = depotChargingPower / tmpBattery.InternalVoltage;
			var connectorLossDep = currentEstDep * (runData.BatteryData?.ConnectionSystemResistance ?? 0.SI<Ohm>()) *
								currentEstDep;
			var etaChgBatDepot = 1 - ((respChgBatDepot.LossPower + connectorLossDep) / respChgBatDepot.PowerDemand).Value();

			var inMotionChargingPower = GetInMotionChargingPower(runData.Mission.MissionType);
			var respInMotionChg = tmpBattery.Request(0.SI<Second>(), 1.SI<Second>(), inMotionChargingPower, true);
			var currentEstInM = inMotionChargingPower / tmpBattery.InternalVoltage;
			var connectorLossInM = currentEstInM * (runData.BatteryData?.ConnectionSystemResistance ?? 0.SI<Ohm>()) *
								currentEstInM;
			var etaChgInMotion = 1 - ((respInMotionChg.LossPower + connectorLossInM) / respInMotionChg.PowerDemand).Value();

			return energyDepot / (energyDepot + energyInMotion) * etaChgBatDepot +
					energyInMotion / (energyDepot + energyInMotion) * etaChgInMotion;
		}

		public static ChargingEfficiencies CalculateChargingEfficiencyIMCOVCHEV(VectoRunData runData, VehicleOperationLookup.VehicleOperationData vehicleOperation,
			WattSecond energyDepot, WattSecond energyInMission, WattSecond energyInMotion)
		{
			var batteryData = runData.BatteryData;
			var depotChargingPower =
				VectoMath.Max(MinDepotChgPwr, batteryData.UseableStoredEnergy / DepotChargingDuration);

            var inMissionChargingPower = VectoMath.Min(
				vehicleOperation.StationaryChargingMaxPwrInfrastructure,
				runData.MaxChargingPower);

			var inMotionChargingPower = GetInMotionChargingPower(runData.Mission.MissionType);

			var tmpBattery = new BatterySystem(null, batteryData);
			var centerSoC = (tmpBattery.MinSoC + tmpBattery.MaxSoC) / 2.0;
			tmpBattery.Initialize(centerSoC);

			var respChgBatDepot = tmpBattery.Request(0.SI<Second>(), 1.SI<Second>(), depotChargingPower, true);
			var respChgBatInMission = tmpBattery.Request(0.SI<Second>(), 1.SI<Second>(), inMissionChargingPower, true);
			var respChgBatInMotion = tmpBattery.Request(0.SI<Second>(), 1.SI<Second>(), inMotionChargingPower, true);

			var currentEstInMission = depotChargingPower / tmpBattery.InternalVoltage;
			var connectorLossInMission = currentEstInMission * batteryData.ConnectionSystemResistance *
								currentEstInMission;
			var currentEstInMotion = inMissionChargingPower / tmpBattery.InternalVoltage;
			var connectorLossInMotion = currentEstInMotion * batteryData.ConnectionSystemResistance *
										currentEstInMotion;
			var currentEstDepot = depotChargingPower / tmpBattery.InternalVoltage;
			var connectorLossDepot = currentEstDepot * batteryData.ConnectionSystemResistance *
								currentEstDepot;

			var etaChgBatDepot = 1 - ((respChgBatDepot.LossPower + connectorLossDepot) / respChgBatDepot.PowerDemand).Value();
			var etaChgBatInMission = 1 - ((respChgBatInMission.LossPower + connectorLossInMission) / respChgBatInMission.PowerDemand).Value();
			var etaChgBatInMotion = 1 - ((respChgBatInMotion.LossPower + connectorLossInMission) / respChgBatInMotion.PowerDemand).Value();

			var totalChargedEnergy = energyDepot + energyInMission + energyInMotion;

			return new ChargingEfficiencies() {
				EtaChargingDepot = etaChgBatDepot,
				EtaChargingInMission = etaChgBatInMission,
				EtaChargingInMotion = etaChgBatInMotion,
				EtaChargingWeighted = energyDepot / totalChargedEnergy * etaChgBatDepot +
									energyInMission / totalChargedEnergy * etaChgBatInMission +
									energyInMotion / totalChargedEnergy * etaChgBatInMotion
			};
		}

		private static Watt GetInMotionChargingPower(MissionType missionType)
		{
			switch (missionType) {
				case MissionType.LongHaul:
				case MissionType.LongHaulEMS:
				case MissionType.RegionalDelivery:
				case MissionType.RegionalDeliveryEMS:
				case MissionType.UrbanDelivery:
				case MissionType.MunicipalUtility:
				case MissionType.Construction:
				case MissionType.Interurban:
				case MissionType.Coach:
				case MissionType.VerificationTest:
				case MissionType.ExemptedMission:
					return 100.SI(Unit.SI.Kilo.Watt).Cast<Watt>();
				case MissionType.HeavyUrban:
				case MissionType.Urban:
				case MissionType.Suburban:
					return 30.SI(Unit.SI.Kilo.Watt).Cast<Watt>();
				default:
					throw new ArgumentOutOfRangeException(nameof(missionType), missionType, null);
			}
		}

		public static IWeightedResult CalculateWeightedSummary(IList<IResultEntry> entries)
		{
			if (entries == null || !entries.Any()) {
				return null;
			}

			if (entries.Sum(x => x.WeightingFactor).IsEqual(0)) {
				return null;
			}

			var fuels = entries.First().FuelData;
			var result = new WeightedResult()
			{
				Status = VectoRun.Status.Success,
				JobType = entries.First().VectoRunData.JobType,
				OffVehicleCharging = false,
				AverageSpeed = null,
				AverageDrivingSpeed = null,
				Distance = entries.Sum(e => e.Distance * e.WeightingFactor),
				Payload = entries.Sum(e => e.Payload * e.WeightingFactor),
				CargoVolume = entries.All(e => e.CargoVolume != null) ? entries.Sum(e => e.CargoVolume * e.WeightingFactor) : 0.SI<CubicMeter>(),
				PassengerCount = entries.All(e => e.PassengerCount != null) ? entries.Sum(e => e.PassengerCount.GetValueOrDefault(0) * e.WeightingFactor) : (double?)null,
				FuelConsumption = fuels.Select(f => Tuple.Create(f,
						entries.All(e => e.FuelConsumptionFinal(f.FuelType) != null) ? entries.Sum(e =>
							e.FuelConsumptionFinal(f.FuelType).TotalFuelConsumptionCorrected * e.WeightingFactor) : null))
					.ToDictionary(x => x.Item1, x => x.Item2),

				FuelConsumptionPerMeter = fuels.Select(f => Tuple.Create(f,
						entries.All(e => e.FuelConsumptionFinal(f.FuelType) != null) ? entries.Sum(e =>
							(e.FuelConsumptionFinal(f.FuelType).TotalFuelConsumptionCorrected / e.Distance) * e.WeightingFactor) : null))
					.ToDictionary(x => x.Item1, x => x.Item2),
				ElectricEnergyConsumption = entries.All(e => e.ElectricEnergyConsumption != null) ? entries.Sum(e => e.ElectricEnergyConsumption * e.WeightingFactor) : null,
				CO2PerMeter = entries.All(e => e.CO2Total != null) ? entries.Sum(e => (e.CO2Total / e.Distance) * e.WeightingFactor) : null,
				ActualChargeDepletingRange = entries.All(e => e.ActualChargeDepletingRange != null) ? entries.Sum(e => e.ActualChargeDepletingRange * e.WeightingFactor) : null,
				EquivalentAllElectricRange = entries.All(e => e.EquivalentAllElectricRange != null) ? entries.Sum(e => e.EquivalentAllElectricRange * e.WeightingFactor) : null,
				ZeroCO2EmissionsRange = entries.All(e => e.ZeroCO2EmissionsRange != null) ? entries.Sum(e => e.ZeroCO2EmissionsRange * e.WeightingFactor) : null,
                HydrogenRange = entries.All(e => e.HydrogenRange != null) ? entries.Sum(e => e.HydrogenRange * e.WeightingFactor) : null,
				BeginOfLifeRanges = new ElectricRangesPEV() {
					ActualChargeDepletingRange = entries.All(e => e.BeginOfLifeRanges.ActualChargeDepletingRange != null) 
						? entries.Sum(e => e.BeginOfLifeRanges.ActualChargeDepletingRange * e.WeightingFactor) 
						: null,
					EquivalentAllElectricRange = entries.All(e => e.BeginOfLifeRanges.EquivalentAllElectricRange != null)
                        ? entries.Sum(e => e.BeginOfLifeRanges.EquivalentAllElectricRange * e.WeightingFactor)
                        : null,
					ZeroCO2EmissionsRange = entries.All(e => e.BeginOfLifeRanges.ZeroCO2EmissionsRange != null)
                        ? entries.Sum(e => e.BeginOfLifeRanges.ZeroCO2EmissionsRange * e.WeightingFactor)
                        : null,
					ElectricEnergyConsumption = entries.All(e => e.BeginOfLifeRanges.ElectricEnergyConsumption != null)
                        ? entries.Sum(e => e.BeginOfLifeRanges.ElectricEnergyConsumption * e.WeightingFactor)
                        : null,
                },
				EndOfLifeRanges = new ElectricRangesPEV()
                {
                    ActualChargeDepletingRange = entries.All(e => e.EndOfLifeRanges.ActualChargeDepletingRange != null)
                        ? entries.Sum(e => e.EndOfLifeRanges.ActualChargeDepletingRange * e.WeightingFactor)
                        : null,
                    EquivalentAllElectricRange = entries.All(e => e.EndOfLifeRanges.EquivalentAllElectricRange != null)
                        ? entries.Sum(e => e.EndOfLifeRanges.EquivalentAllElectricRange * e.WeightingFactor)
                        : null,
                    ZeroCO2EmissionsRange = entries.All(e => e.EndOfLifeRanges.ZeroCO2EmissionsRange != null)
                        ? entries.Sum(e => e.EndOfLifeRanges.ZeroCO2EmissionsRange * e.WeightingFactor)
                        : null,
                    ElectricEnergyConsumption = entries.All(e => e.EndOfLifeRanges.ElectricEnergyConsumption != null)
                        ? entries.Sum(e => e.EndOfLifeRanges.ElectricEnergyConsumption * e.WeightingFactor)
                        : null,
                },
                UtilityFactor = double.NaN,

                AuxHeaterFuel = entries.First().AuxHeaterFuel,
				ZEV_CO2 = entries.Sum(e => ((e?.ZEV_CO2 ?? 0.SI<Kilogram>()) / e.Distance) * e.WeightingFactor),
				ZEV_FuelConsumption_AuxHtr = entries.Sum(e => ((e?.ZEV_FuelConsumption_AuxHtr ?? 0.SI<Kilogram>()) / e.Distance) * e.WeightingFactor),
			};

			return result;
		}

		public static IWeightedResult CalculateWeightedSummary(IList<IOVCResultEntry> entries)
		{
			if (entries == null || !entries.Any()) {
				return null;
			}

			if (entries.Any(e => e.Weighted == null)) {
				return null;
			}

			var fuels = entries.First().ChargeDepletingResult.FuelData;
			return new WeightedResult()
			{
				Status = VectoRun.Status.Success,
				JobType = entries.First().Weighted.JobType,
				OffVehicleCharging = true,
				AverageSpeed = null,
				AverageDrivingSpeed = null,
				Distance = entries.Sum(e => e.ChargeDepletingResult.Distance * e.ChargeDepletingResult.WeightingFactor),
				Payload = entries.Sum(e => e.ChargeDepletingResult.Payload * e.ChargeDepletingResult.WeightingFactor),
				CargoVolume = entries.All(e => e.ChargeDepletingResult.CargoVolume != null) ? entries.Sum(e => e.ChargeDepletingResult.CargoVolume * e.ChargeDepletingResult.WeightingFactor) : 0.SI<CubicMeter>(),
				PassengerCount = entries.All(e => e.ChargeDepletingResult.PassengerCount != null) ? entries.Sum(e => e.ChargeDepletingResult.PassengerCount.Value * e.ChargeDepletingResult.WeightingFactor) : (double?)null,
				FuelConsumption = fuels.Select(f => Tuple.Create(f,
						entries.Sum(e =>
							e.Weighted.FuelConsumption[f] * e.ChargeDepletingResult.WeightingFactor)))
					.ToDictionary(x => x.Item1, x => x.Item2),
				FuelConsumptionPerMeter = fuels.Select(f => Tuple.Create(f,
						entries.Sum(e => e.Weighted.FuelConsumptionPerMeter[f] * e.ChargeDepletingResult.WeightingFactor)))
						.ToDictionary(x => x.Item1, x => x.Item2),
                ElectricEnergyConsumption = entries.Sum(e => e.Weighted.ElectricEnergyConsumption * e.ChargeDepletingResult.WeightingFactor),
				CO2PerMeter = entries.All(e => e.Weighted.CO2PerMeter != null) ? entries.Sum(e => (e.Weighted.CO2PerMeter) * e.ChargeDepletingResult.WeightingFactor) : null,
				ActualChargeDepletingRange = entries.Sum(e => e.Weighted.ActualChargeDepletingRange * e.ChargeDepletingResult.WeightingFactor),
				EquivalentAllElectricRange = entries.Sum(e => e.Weighted.EquivalentAllElectricRange * e.ChargeDepletingResult.WeightingFactor),
				ZeroCO2EmissionsRange = entries.Where(e => e.Weighted.ZeroCO2EmissionsRange != null).Sum(e => e.Weighted.ZeroCO2EmissionsRange * e.ChargeDepletingResult.WeightingFactor),
				HydrogenRange = entries.Where(e => e.Weighted.HydrogenRange != null).Sum(e => e.Weighted.HydrogenRange * e.ChargeDepletingResult.WeightingFactor),
                BeginOfLifeRanges = new ElectricRangesPEV()
                {
                    ActualChargeDepletingRange = entries.Where(e => e.Weighted.BeginOfLifeRanges.ActualChargeDepletingRange != null)
                        .Sum(e => e.Weighted.BeginOfLifeRanges.ActualChargeDepletingRange * e.ChargeDepletingResult.WeightingFactor),
                    EquivalentAllElectricRange = entries.Where(e => e.Weighted.BeginOfLifeRanges.EquivalentAllElectricRange != null)
                        .Sum(e => e.Weighted.BeginOfLifeRanges.EquivalentAllElectricRange * e.ChargeDepletingResult.WeightingFactor),
                    ZeroCO2EmissionsRange = entries.Where(e => e.Weighted.BeginOfLifeRanges.ZeroCO2EmissionsRange != null)
                        .Sum(e => e.Weighted.BeginOfLifeRanges.ZeroCO2EmissionsRange * e.ChargeDepletingResult.WeightingFactor),
                    ElectricEnergyConsumption = entries.Where(e => e.Weighted.BeginOfLifeRanges.ElectricEnergyConsumption != null)
                        .Sum(e => e.Weighted.BeginOfLifeRanges.ElectricEnergyConsumption * e.ChargeDepletingResult.WeightingFactor),
                },
                EndOfLifeRanges = new ElectricRangesPEV()
                {
                    ActualChargeDepletingRange = entries.Where(e => e.Weighted.EndOfLifeRanges.ActualChargeDepletingRange != null)
                        .Sum(e => e.Weighted.EndOfLifeRanges.ActualChargeDepletingRange * e.ChargeDepletingResult.WeightingFactor),
                    EquivalentAllElectricRange = entries.Where(e => e.Weighted.EndOfLifeRanges.EquivalentAllElectricRange != null)
                        .Sum(e => e.Weighted.EndOfLifeRanges.EquivalentAllElectricRange * e.ChargeDepletingResult.WeightingFactor),
                    ZeroCO2EmissionsRange = entries.Where(e => e.Weighted.EndOfLifeRanges.ZeroCO2EmissionsRange != null)
                        .Sum(e => e.Weighted.EndOfLifeRanges.ZeroCO2EmissionsRange * e.ChargeDepletingResult.WeightingFactor),
                    ElectricEnergyConsumption = entries.Where(e => e.Weighted.EndOfLifeRanges.ElectricEnergyConsumption != null)
                        .Sum(e => e.Weighted.EndOfLifeRanges.ElectricEnergyConsumption * e.ChargeDepletingResult.WeightingFactor),
                },
                UtilityFactor = double.NaN,

                AuxHeaterFuel = entries.First().ChargeDepletingResult.AuxHeaterFuel,
				ZEV_CO2 = entries.Sum(e => (e?.Weighted?.ZEV_CO2 ?? 0.SI<KilogramPerMeter>()) * e.ChargeDepletingResult.WeightingFactor),
				ZEV_FuelConsumption_AuxHtr = entries.Sum(e => (e?.Weighted?.ZEV_FuelConsumption_AuxHtr ?? 0.SI<KilogramPerMeter>()) * e.ChargeDepletingResult.WeightingFactor),
			};
		}

        public static ElectricRangesPEV CalculateElectricRanges(VectoRunData runData, IModalDataContainer data, double deterioration)
        {
            return runData.InMotionCharging
                ? DoCalculateElectricRangesIMCWithDeterioration(data, runData, deterioration)
                : DoCalculateElectricRangesWithDeterioration(data.CorrectedModalData.ElectricEnergyConsumption_SoC_Corr,
                    data.Distance, CalculateChargingEfficiencyPEV(runData), runData, deterioration);
        }

        public static ElectricRangesPEV CalculateElectricRangesPEV(VectoRunData runData, IModalDataContainer data)
		{
			return runData.InMotionCharging
				? DoCalculateElectricRangesIMCPEV(data, runData, runData.BatteryData)
				: DoCalculateElectricRangesPEV(data.CorrectedModalData.ElectricEnergyConsumption_SoC_Corr,
					data.Distance, CalculateChargingEfficiencyPEV(runData), runData.BatteryData);
		}

		public static ElectricRangesPEV CalculateElectricRangesPEVCompletedBus(BatterySystemData batteryData,
			WattSecond ElectricEnergyConsumptionSoc, Meter distance)
		{
			return DoCalculateElectricRangesPEV(electricEnergyConsumptionSoCCorr: ElectricEnergyConsumptionSoc,
				distance: distance, chargingEfficiencyBattery: 1, batteryData);
		}

		public static ElectricRangesPEV CalculateElectricRangesCompletedBus(
            WattSecond ElectricEnergyConsumptionSoc, 
			Meter distance,
			VectoRunData runData, 
			double deterioration)
		{
            return DoCalculateElectricRangesWithDeterioration(ElectricEnergyConsumptionSoc,
                    distance, chargingEfficiencyBattery: 1, runData, deterioration);
        }

        private static ElectricRangesPEV DoCalculateElectricRangesWithDeterioration(
			WattSecond electricEnergyConsumptionSoCCorr, 
			Meter distance, 
			double chargingEfficiencyBattery, 
			VectoRunData runData,
			double deterioration)
		{
			var vehicle = (runData.InputData is IMultistepBusInputDataProvider)
				? (runData.InputData as IMultistepBusInputDataProvider).JobInputData.PrimaryVehicle.Vehicle
				: runData.InputData.JobInputData.Vehicle;
			
            var batteryData = new ElectricStorageAdapter().CreateBatteryData(
                vehicle.Components.ElectricStorage, 
				runData.JobType, 
				vehicle.OVC,
				vehicle.BatteryOnlyMode,
				deterioration);

            return DoCalculateElectricRangesPEV(electricEnergyConsumptionSoCCorr, distance, chargingEfficiencyBattery, batteryData);
        }

        private static ElectricRangesPEV DoCalculateElectricRangesPEV(WattSecond electricEnergyConsumptionSoCCorr, Meter distance, double chargingEfficiencyBattery, BatterySystemData runDataBatteryData)
		{
			var batteryData = runDataBatteryData;
			if (batteryData == null) {
				throw new VectoException("Battery Data is required for PEV range calculation");
			}

			var D9_chargingEfficiencyBattery = chargingEfficiencyBattery;
			var D15_useableBatteryCapacityForR_CDA = batteryData.UseableStoredEnergy;
			var D13_electricEnergyConsumption = electricEnergyConsumptionSoCCorr;

			var D16_actualChargeDepletingRange = D15_useableBatteryCapacityForR_CDA / D13_electricEnergyConsumption * distance;
			var D17_equivalentAllElectricRange = D16_actualChargeDepletingRange;
			var D18_zeroCO2EmissionsRange = D17_equivalentAllElectricRange;

			var D21_electricEnergyConsumptionWeighted = D13_electricEnergyConsumption / D9_chargingEfficiencyBattery;

			var retVal = new ElectricRangesPEV {
				ActualChargeDepletingRange = D16_actualChargeDepletingRange,
				EquivalentAllElectricRange = D17_equivalentAllElectricRange,
				ZeroCO2EmissionsRange = D18_zeroCO2EmissionsRange,
				ElectricEnergyConsumption = D21_electricEnergyConsumptionWeighted,
			};
			return retVal;
		}

        internal static ElectricRangesPEV DoCalculateElectricRangesIMCWithDeterioration(IModalDataContainer modData, VectoRunData runData, double deterioration)
		{
			var batteryData = new ElectricStorageAdapter().CreateBatteryData(
                runData.InputData.JobInputData.Vehicle.Components.ElectricStorage,
                runData.JobType,
                runData.VehicleData.OffVehicleCharging,
				runData.InputData.JobInputData.Vehicle.BatteryOnlyMode,
                deterioration);

            return DoCalculateElectricRangesIMCPEV(modData, runData, batteryData);
        }

        internal static ElectricRangesPEV DoCalculateElectricRangesIMCPEV(IModalDataContainer modData, VectoRunData runData, BatterySystemData batteryData)
		{
			if (batteryData == null) {
				throw new VectoException("Battery Data is required for PEV range calculation");
			}

			var distance = modData.Distance;
			var electricEnergyConsumptionSoCCorr = modData.CorrectedModalData.ElectricEnergyConsumption_SoC_Corr;

			// runData.Mission.BusParameter?.BusGroup ?? runData.VehicleData.VehicleClass
            var vehicleOperation = VehicleOperation.LookupVehicleOperation(runData.Mission.BusParameter?.BusGroup ?? runData.VehicleData.VehicleClass, runData.Mission.MissionType);

			var D9_useableBatteryCapacityForR_CDA = batteryData.UseableStoredEnergy;
			var D10_electricEnergyConsumption = electricEnergyConsumptionSoCCorr / distance;

			var D12_actualChargeDepletingRange = D9_useableBatteryCapacityForR_CDA / D10_electricEnergyConsumption;
			var D13_equivalentAllElectricRange = D12_actualChargeDepletingRange;
			var D14_zeroCO2EmissionsRange = D13_equivalentAllElectricRange;

			var D16_dailySpecificMileage = vehicleOperation.Mileage.DailyMileage;
			var D17_RealWorldFactorUsageStartSoC = vehicleOperation.RealWorldUsageFactors.StartSoCBeforeMission;
			var D18_shareInMotionChargingInfrastructure = GetShareIMCInfrastructure(runData.InMotionChargingTechnology, vehicleOperation);
			var D19_realWorkdFactorInMotionChargingDuringMission =
				vehicleOperation.RealWorldUsageFactors.InMotionChargingDuringMission;

			var D21_electricEnergyFromStartSoCDepot = D17_RealWorldFactorUsageStartSoC * D9_useableBatteryCapacityForR_CDA;
			var D22_electricEnergyDirectFeed = D18_shareInMotionChargingInfrastructure * D10_electricEnergyConsumption * D16_dailySpecificMileage;
			var D23_electricEnergyChargedInMotion = D19_realWorkdFactorInMotionChargingDuringMission * D9_useableBatteryCapacityForR_CDA;

			var D25_electricEnergyReqForDailyMileage = D10_electricEnergyConsumption  * D16_dailySpecificMileage;
			var D26_LimitaionOfElectricEnergyCharged =
				VectoMath.Max(D25_electricEnergyReqForDailyMileage - D22_electricEnergyDirectFeed, 0.SI<WattSecond>());

			var D28_shareElectricEnergyFromGrid = D26_LimitaionOfElectricEnergyCharged / D25_electricEnergyReqForDailyMileage;
			var D29_averageChgEffExternalCharging = CalculateChargingEfficiencyIMCPEV(runData, D21_electricEnergyFromStartSoCDepot, D23_electricEnergyChargedInMotion);
			var D30_shareElectridEnergyGridDirectFeed = 1 - D28_shareElectricEnergyFromGrid;
			var D31_AverageDischargingEfficiencyBattery = modData.BatteryEfficiencyDischarge();

			var D33_CorrectionFactorEC_SoC_to_EC_Terminal = D28_shareElectricEnergyFromGrid*(1/D29_averageChgEffExternalCharging) + D30_shareElectridEnergyGridDirectFeed* D31_AverageDischargingEfficiencyBattery;

			var D35_EC_el_Final = D10_electricEnergyConsumption * D33_CorrectionFactorEC_SoC_to_EC_Terminal * distance;

			var retVal = new ElectricRangesPEV {
				ActualChargeDepletingRange = D12_actualChargeDepletingRange,
				EquivalentAllElectricRange = D13_equivalentAllElectricRange,
				ZeroCO2EmissionsRange = D14_zeroCO2EmissionsRange,
				ElectricEnergyConsumption = D35_EC_el_Final,
			};
			return retVal;
		}

		public static double GetShareIMCInfrastructure(IMCTechnology imcTech,
			VehicleOperationLookup.VehicleOperationData vehicleOperationData)
		{
			switch (imcTech) {
				case IMCTechnology.NotApplicable:
					return double.NaN;
				case IMCTechnology.OverheadPantograph:
					return vehicleOperationData.ShareInMotionCharging.ShareCatenary;
				case IMCTechnology.OverheadTrolley:
					return vehicleOperationData.ShareInMotionCharging.ShareTrolley;
				case IMCTechnology.GroundRail:
					return vehicleOperationData.ShareInMotionCharging.ShareGroundRail;
				case IMCTechnology.Wireless:
					return vehicleOperationData.ShareInMotionCharging.ShareWireless;
				default:
					throw new ArgumentOutOfRangeException();
			}
		}

		public struct ElectricRangesPEV
		{
			public Meter ZeroCO2EmissionsRange { get; set; }
			public Meter ActualChargeDepletingRange { get; set; }
			public Meter EquivalentAllElectricRange { get; set; }
			public WattSecond ElectricEnergyConsumption { get; set; }
		}

		public struct ChargingEfficiencies
		{
			public double EtaChargingDepot { get; set; }
			public double EtaChargingInMission { get; set; }
			public double EtaChargingInMotion { get; set; }
			public double EtaChargingWeighted { get; set; }
		}

	}
}
