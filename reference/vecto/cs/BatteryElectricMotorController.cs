using System.Linq;
using TUGraz.VectoCommon.InputData;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Configuration;
using TUGraz.VectoCore.Models.Simulation;
using TUGraz.VectoCore.Models.Simulation.DataBus;
using TUGraz.VectoCore.Models.SimulationComponent.Data;
using TUGraz.VectoCore.Utils;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
    public class BatteryElectricMotorController : IElectricMotorControl
	{
		protected IVehicleContainer DataBus;
		private IElectricSystem ElectricSystem;
		protected ElectricMotorData ElectricMotorData;

		protected readonly GearboxData GearboxModelData;

		public int AxleNumber {  get; private set; }

		public BatteryElectricMotorController(IVehicleContainer container, IElectricSystem es, AxlePowertrainData axlePt = null)
		{
			DataBus = container;
			ElectricMotorData = (axlePt == null) ? container.RunData.ElectricMachinesSinglePwt.FirstOrDefault()?.Item2 : axlePt.ElectricMachineData.Item2;
			ElectricSystem = es;
			GearboxModelData = (axlePt == null) ? container.RunData.GearboxSinglePwt : axlePt.GearboxData;
			AxleNumber = (axlePt == null) ? Constants.NOT_IN_AXLE_POWERTRAIN : axlePt.AxleNumber;
		}

		#region Implementation of IElectricMotorControl

		public NewtonMeter MechanicalAssistPower(Second absTime, Second dt, NewtonMeter outTorque, 
			PerSecond prevOutAngularVelocity, PerSecond currOutAngularVelocity, NewtonMeter maxDriveTorque, 
			NewtonMeter maxRecuperationTorque, PowertrainPosition position, bool dryRun)
		{
			var gearbox = DataBus.GearboxesInfo.First(x => x.AxleNumber == AxleNumber);

			if (!gearbox.GearEngaged(absTime) && DataBus.DriverInfo.DrivingAction == DrivingAction.Roll) {
				var avgSpeed = (prevOutAngularVelocity + currOutAngularVelocity) / 2;
				var inertiaTorqueLoss = avgSpeed.IsEqual(0)
					? 0.SI<NewtonMeter>()
					: Formulas.InertiaPower(currOutAngularVelocity, prevOutAngularVelocity, 
						ElectricMotorData.Inertia, dt) / avgSpeed;
				//var dragTorque = ElectricMotorData.DragCurve.Lookup()
				//return ((-1)*(inertiaTorqueLoss + outTorque)).LimitTo(maxDriveTorque, maxRecuperationTorque ?? VectoMath.Max(maxDriveTorque, 0.SI<NewtonMeter>())); //.LimitTo(maxDriveTorque, maxRecuperationTorque);
				return -inertiaTorqueLoss;
			}
            if (DataBus.DriverInfo.DrivingAction == DrivingAction.Coast ||
                DataBus.DriverInfo.DrivingAction == DrivingAction.Roll) {
                return null;
            }
			
            if (CannotProvideRecuperationAtLowSpeed(outTorque)) {
                return null;
            }

            if (maxDriveTorque == null) {
				return null;
			}

			return (-outTorque).LimitTo(maxDriveTorque, maxRecuperationTorque ?? VectoMath.Max(maxDriveTorque, 0.SI<NewtonMeter>()));
        }

        #endregion

        protected virtual bool CannotProvideRecuperationAtLowSpeed(NewtonMeter outTorque)
		{
			var driverIsBraking = DataBus.DriverInfo.DriverBehavior == DrivingBehavior.Braking &&
								DataBus.DriverInfo.DrivingAction == DrivingAction.Brake;

            return driverIsBraking && (DataBus.VehicleInfo.VehicleSpeed ?? 0.SI<MeterPerSecond>()).IsSmallerOrEqual(
				GearboxModelData?.DisengageWhenHaltingSpeed ?? Constants.SimulationSettings.ATGearboxDisengageWhenHaltingSpeed)
					&& outTorque.IsSmaller(0);
		}

    }
}