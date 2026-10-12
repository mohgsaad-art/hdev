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
using TUGraz.VectoCommon.Utils;

namespace TUGraz.VectoCore.Configuration
{
	public static class Constants
	{
		public const string NOT_AVAILABLE = "N/A";
        public const int NOT_IN_AXLE_POWERTRAIN = -1;

        public static Second DefaultPowerShiftTime = 0.8.SI<Second>();
		public const double RPMToRad = 2 * Math.PI / 60;
		public const double Kilo = 1000;
		public const double MeterPerSecondToKMH = 3.6;
		public const int Mega = 1000000;

		public static class Auxiliaries
		{
			public const string Cycle = "cycle";
			public const string Prefix = "AUX_";
			public const string PowerPrefix = "P_";

			public static class IDs
			{
				public const string PTOTransmission = "PTO_TRANSM";
				public const string PTORoadsweeping = "PTO_RoadSweeping";
				public const string PTODuringDrive = "PTO_DuringDrive";
				public const string Fan = "FAN";
				public const string SteeringPump = "STP";
				public const string SteeringPump_el = "STP";
				public const string ElectricSystem = "ES";
				public const string HeatingVentilationAirCondition = "AC";
				public const string PneumaticSystem = "PS";
				public const string Cond = "COND";
				public const string PTOConsumer = "PTO_CONSUM";

				/// <summary>
				/// Engineering Mode
				/// </summary>
				public const string ENGMode_AUX_MECH_BASE = "ENG_AUX_BASE";
				public const string ENGMode_AUX_MECH_FAN = "ENG_AUX_FAN";
				public const string ENGMode_AUX_MECH_STP = "ENG_AUX_STP";

				// High voltage auxiliaries
				public const string PowerAdditonalHighVoltage = "Padd_hv";
				public const string PowerAuxiliaryElectric = "P_aux_el";
			}

			public static class Names
			{
				public const string Fan = "Fan";
				public const string SteeringPump = "Steering pump";
				public const string ElectricSystem = "Electric System";
				public const string HeatingVentilationAirCondition = "HVAC";
				public const string PneumaticSystem = "Pneumatic System";
			}
		}

		public static class BusAuxiliaries
		{
			public static class SteadyStateModel
			{
				public static readonly Kelvin PassengerBoundaryTemperature = 17.0.DegCelsiusToKelvin();
				public const double SolarCloudingLow = 0.65;
				public const double SolarCloudingHigh = 0.8;
				public static readonly Watt HeatPerPassengerIntoCabinLow = 50.SI<Watt>();
				public static readonly Watt HeatPerPassengerIntoCabinHigh = 80.SI<Watt>();

				public static readonly Kelvin MaxTemperatureDeltaForLowFloorBusses = 3.SI<Kelvin>();
				public const double MaxPossibleBenefitFromTechnologyList = 0.5;

				public static readonly Kelvin HeatingBoundaryTemperature = 18.0.DegCelsiusToKelvin();
				public static readonly Kelvin CoolingBoundaryTemperature = 23.0.DegCelsiusToKelvin();

				public static readonly PerSecond HighVentilation = 20.SI(Unit.SI.Per.Hour).Cast<PerSecond>();
				public static readonly PerSecond HighVentilationHeating = 10.SI(Unit.SI.Per.Hour).Cast<PerSecond>();
				public static readonly PerSecond LowVentilation = 7.SI(Unit.SI.Per.Hour).Cast<PerSecond>();

				public const double AuxHeaterEfficiency = 0.84;

				public static readonly JoulePerCubicMeter SpecificVentilationPower =
					0.56.SI(Unit.SI.Watt.Hour.Per.Cubic.Meter).Cast<JoulePerCubicMeter>();

				public const double GFactor = 0.95;

				public static readonly Kelvin DefaultTemperature = 25.0.DegCelsiusToKelvin();
				public static readonly WattPerSquareMeter DefaultSolar = 400.SI<WattPerSquareMeter>();
			}

			public static class ElectricSystem
			{
				public static readonly Volt PowernetVoltage = 28.3.SI<Volt>();

				public const double AlternatorGearEfficiency = 1;

				public const double StoredEnergyEfficiency = 0.935;
			}

			public static class ElectricConstants
			{
				// Anticipated Min and Max Allowable values for Powernet, normally 26.3 volts but could be 48 in the future.
				public const double PowenetVoltageMin = 6;
				public const double PowenetVoltageMax = 50;

				// Duty Cycle IE Percentage of use
				public const double PhaseIdleTractionOnMin = 0;
				public const double PhaseIdleTractionMax = 1;

				// Max Min Expected Consumption for a Single Consumer, negative values allowed as bonuses.
				public const int NonminalConsumerConsumptionAmpsMin = -10;
				public const int NominalConsumptionAmpsMax = 100;


				// Alternator
				public const double AlternatorPulleyEfficiencyMin = 0.1;
				public const double AlternatorPulleyEfficiencyMax = 1;
			}

			public static class ElectricalConsumers
			{
				public const string DoorsPerVehicleConsumer = "Doors per vehicle";
				public static readonly Second DoorActuationTimeSecond = 4.SI<Second>();
			}

			public static class PneumaticConsumersDemands
			{
				public static readonly NormLiterPerSecond AdBlueInjection =
					21.25.SI(Unit.SI.Liter.Per.Minute).Cast<NormLiterPerSecond>();

				public static readonly NormLiterPerSecond AirControlledSuspension =
					15.SI(Unit.SI.Liter.Per.Minute).Cast<NormLiterPerSecond>();

				public static readonly NormLiterPerKilogram BrakingNoRetarder =
					0.00081.SI(Unit.SI.Liter.Per.Kilo.Gramm).Cast<NormLiterPerKilogram>();

				public static readonly NormLiterPerKilogram BrakingWithRetarder =
					0.0006.SI(Unit.SI.Liter.Per.Kilo.Gramm).Cast<NormLiterPerKilogram>();

				public static readonly NormLiterPerKilogramMeter BreakingAndKneeling =
					0.000066.SI(Unit.SI.Liter.Per.Kilo.Gramm.Milli.Meter).Cast<NormLiterPerKilogramMeter>();

				// Nl (blowout) / Nl (DeadVolume) / h -> 1/s
				public static readonly PerSecond DeadVolBlowOuts = 24.SI(Unit.SI.Per.Hour).Cast<PerSecond>();
				public static readonly NormLiter DeadVolume = 30.SI<NormLiter>();
				public static readonly double NonSmartRegenFractionTotalAirDemand = 0.26;
				public static readonly double SmartRegenFractionTotalAirDemand = 0.12;
				public static readonly double OverrunUtilisationForCompressionFraction = 0.97;
				public static readonly NormLiter DoorOpening = 12.7.SI<NormLiter>();

				public static readonly NormLiterPerKilogram StopBrakeActuation =
					0.00064.SI(Unit.SI.Liter.Per.Kilo.Gramm).Cast<NormLiterPerKilogram>();

			}

			public static class PneumaticUserConfig
			{
				public static readonly Meter DefaultKneelingHeight = 80.SI(Unit.SI.Milli.Meter).Cast<Meter>();
				public const double CompressorGearRatio = 1.0;
				public const double CompressorGearEfficiency = 0.97;

				public const double PneumaticOverrunUtilisation = 0.97;

				public const double ViscoClutchDragCurveFactor = 1 - 0.35;
				public const double MechanicClutchDragCurveFactor = 1 - 0.75;
			}

			public static class Heater {
				public const double CoolantHeatTransferredToAirCabinHeater = 0.75;
				public const double FuelEnergyToHeatToCoolant = 0.2;
				public const double ElectricWasteHeatToCoolant = 0.9;
			}
		}

		public static class BusParameters
		{
			public static readonly Meter DriverCompartmentLength = 1.2.SI<Meter>();

			public static readonly Kilogram PassengerWeightLow = 68.SI<Kilogram>();
			public static readonly Kilogram PassengerWeightHigh = 71.SI<Kilogram>();

			public static readonly Meter WindowHeightSingleDecker = 1.5.SI<Meter>();
			public static readonly Meter WindowHeightDoubleDecker = 2.5.SI<Meter>();

			public static readonly SquareMeter FrontAndRearWindowAreaSingleDecker = 5.SI<SquareMeter>();
			public static readonly SquareMeter FrontAndRearWindowAreaDoubleDecker = 8.SI<SquareMeter>();

			public static readonly Meter InternalHeightDoubleDecker = 1.8.SI<Meter>();
			public static readonly Meter HeightLuggageCompartment = 0.5.SI<Meter>();
			public static readonly SIBase<Meter> EntranceHeight = 0.27.SI<Meter>();

			public static readonly MeterPerSecond MaxBusSpeed = 103.KMPHtoMeterPerSecond();

			public static readonly Meter VehicleWidthLow = 2.5.SI<Meter>();
			public static readonly Meter VehicleWidthHigh = 2.55.SI<Meter>();

			public static class Auxiliaries
			{
				public static class SteeringPump
				{
					public static readonly SI TubingLoss = 52000.SI(Unit.SI.Kilo.Gramm.Per.Square.Second.Square.Meter);
					public static readonly Meter LengthBonus = 1.2.SI<Meter>();
					public static readonly SI VolumeFlow = 16.SI(Unit.SI.Cubic.Dezi.Meter.Per.Minute);

				}
			}
		}

		public static class FileExtensions
		{
			public const string PDFReport = ".pdf";
			public const string ModDataFile = ".vmod";

			public const string SumFile = ".vsum";

			public const string VectoJobFile = ".vecto";

			public const string VectoXMLDeclarationFile = ".xml";

			public const string EngineDataFile = ".veng";

			public const string VehicleDataFile = ".vveh";

			public const string GearboxDataFile = ".vgbx";

			public const string GearshiftDataFile = ".vtcu";

			public const string BatteryFile = ".vreess";

			public const string ElectricMotorFile = ".vem";

			public const string CycleFile = ".vdri";

			public const string DriverAccelerationCurve = ".vacc";

			public const string HybridStrategyParameters = ".vhctl";

			public const string Json = ".json";

			public const string IEPCDataFile = ".viepc";

			public const string FuelCellComponentFile = ".vfcc";

		}

		public static class SimulationSettings
		{
			/// <summary>
			/// base time interval for the simulation. the distance is estimated to reach this time interval as good as possible
			/// </summary>
			public static readonly Second TargetTimeInterval = 0.5.SI<Second>();

			/// <summary>
			/// maximum time interval for the simulation in measured speed mode.
			/// </summary>
			public static readonly Second MeasuredSpeedTargetTimeInterval = 1.SI<Second>();

			/// <summary>
			/// The lower time bound before braking is initiated.
			/// </summary>
			public static readonly Second LowerBoundTimeInterval = 0.25.SI<Second>();

			/// <summary>
			/// simulation interval if the vehicle stands still
			/// </summary>
			public static readonly Meter DriveOffDistance = 0.25.SI<Meter>();

			public static readonly Meter BrakeNextTargetDistance = 2.5.SI<Meter>();

			/// <summary>
			/// used in DriverModeBrake to detect if a vehicle is already below the speed of the brake trigger.
			/// </summary>
			public static readonly MeterPerSecond BrakeTriggerSpeedTolerance = 0.1.KMPHtoMeterPerSecond();
			
			public static readonly MeterPerSecond MinVelocityForCoast = 5.KMPHtoMeterPerSecond();

			/// <summary>
			/// threshold for changes in the road gradient. changes below this threshold will be considered to be equal for filtering out the driving cycle.
			/// altitude computation is done before filtering! 
			/// </summary>
			public static readonly Radian DrivingCycleRoadGradientTolerance = 1E-12.SI<Radian>();

			/// <summary>
			/// Tolerance for searching operating point with line search.
			/// </summary>
			public const double LineSearchTolerance = 0.5;

			/// <summary>
			/// Tolerance for searching operating point with interpolating search.
			/// </summary>
			public const double InterpolateSearchTolerance = 1e-3;

			public const double ClutchClosingSpeedNorm = 0.065;

			public static readonly MeterPerSecond ClutchDisengageWhenHaltingSpeed = 10.KMPHtoMeterPerSecond();

			public static readonly MeterPerSecond ATGearboxDisengageWhenHaltingSpeed = 5.KMPHtoMeterPerSecond();

			public static readonly Meter DriverActionDistanceTolerance = 0.25.SI<Meter>();

			public static readonly MeterPerSecond VehicleSpeedHaltTolerance = 2e-3.SI<MeterPerSecond>();

			/// <summary>
			/// The initial search interval for the operating point search in the driver.
			/// </summary>
			public static readonly MeterPerSquareSecond OperatingPointInitialSearchIntervalAccelerating =
				0.09.SI<MeterPerSquareSecond>();

			public static readonly PerSecond EngineIdlingSearchInterval = 10.SI<PerSecond>();

			public const int MaximumIterationCountForSimulationStep = 30;

			public static readonly Meter GearboxLookaheadForAccelerationEstimation = 100.SI<Meter>();

			public static readonly Kilogram MaximumGrossVehicleMass = 40000.SI<Kilogram>();
			public static readonly Kilogram MaximumGrossVehicleMassOVCHev_NaturalGas = 41000.SI<Kilogram>();
			public static readonly Kilogram MaximumGrossVehicleMassPEV = 42000.SI<Kilogram>();
			public static readonly Kilogram MaximumGrossVehicleMassEMS = 60000.SI<Kilogram>();
			public static readonly Kilogram MaximumGrossVehicleMassEMS_OVCHev_NaturalGas = 61000.SI<Kilogram>();
			public static readonly Kilogram MaximumGrossVehicleMassEMS_PEV = 62000.SI<Kilogram>();

			public static readonly MeterPerSecond HighwaySpeedThreshold = 70.KMPHtoMeterPerSecond();
			public static readonly MeterPerSecond RuralSpeedThreshold = 50.KMPHtoMeterPerSecond();

			public static readonly Second ThresholdStandstillOff = 10.SI<Second>();

			public static class CrosswindCorrection
			{
				public const int MinVehicleSpeed = 60; // km/h
				public const int MaxVehicleSpeed = 130; // km/h
				public const int VehicleSpeedStep = 5; // km/h

				public const int MaxAlpha = 180; // degree
				public const int AlphaStep = 10; // degree

				public const int MinHeight = 5; // percent
				public const int MaxHeight = 100; // percent
				public const int HeightStep = 10; // percent
			}
			/// <summary>
			/// When the simulated (in VTP) positive engine work deviates more than this threshold
			/// from the measured positive energy of the vdri, a warning is issued.
			/// </summary>
			public const double VTPEngineWorkDeviationThreshold = 0.1;

			/// <summary>
			/// When the engine speed (in VTP) is higher than idle speed times this factor,
			/// the combustion engine is set to on.
			/// </summary>
			public const double VTPIdleSpeedDetectionFactor = 0.85;
		}

		public static class XML
		{
			public const string XSDDeclarationVersion = "1.0";
			public const string XSDEngineeringVersion = "0.7";

			public const string DeclarationNSPrefix = "vdd";

			public const string EngineeringNSPrefix = "ved";

			public const string RootNSPrefix = "tns";

			public const string VectoDeclarationDefinitionsNS =
				"urn:tugraz:ivt:VectoAPI:DeclarationDefinitions:v" + XSDDeclarationVersion;

			public const string VectoDeclarationComponentNS = "urn:tugraz:ivt:VectoAPI:DeclarationComponent:v" + XSDDeclarationVersion;

			public const string VectoEngineeringDefinitionsNS =
				"urn:tugraz:ivt:VectoAPI:EngineeringDefinitions:v" + XSDEngineeringVersion;

			public const string VectoDeclarationInputNS = "urn:tugraz:ivt:VectoAPI:DeclarationInput:v" + XSDDeclarationVersion;

			public const string VectoEngineeringInputNS = "urn:tugraz:ivt:VectoAPI:EngineeringInput:v" + XSDEngineeringVersion;
		}

		public static class GenericLossMapSettings
		{
			public const double OutputSpeedStart = 50;
			public const double OutputSpeedEnd = 5000;

			public const double OutputTorqueStart = 250;
			public const double OutputTorqueEnd = 500000;

			public const double Efficiency = 0.98;

			public const double T0 = 52.5;
			public const double T1 = 15;
			public const double Td_n = 150;

			public const double FactorAngleDrive = 0.75;

			public const double RetarderGenericFactor = 1;
		}

		public static class PowerMapSettings
		{
			public const double EfficiencyMapExtrapolationFactor = 1.2f;
		}

		public static class EMFullLoadCurveSettings
		{
			public const double RatedSpeedGradientDelta = 0.2f;
		}
	}
}