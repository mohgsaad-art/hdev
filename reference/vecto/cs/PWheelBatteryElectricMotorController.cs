using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Configuration;
using TUGraz.VectoCore.Models.Simulation;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
    public class PWheelBatteryElectricMotorController : BatteryElectricMotorController
    {
        public PWheelBatteryElectricMotorController(IVehicleContainer container, IElectricSystem es) : base(container, es)
        {}

        protected override bool CannotProvideRecuperationAtLowSpeed(NewtonMeter outTorque)
        {
           return DataBus.DrivingCycleInfo.CycleData.LeftSample.VehicleTargetSpeed.IsSmallerOrEqual(
				GearboxModelData?.DisengageWhenHaltingSpeed ?? Constants.SimulationSettings.ClutchDisengageWhenHaltingSpeed)
					&& outTorque.IsSmaller(0);
        }
    }
}
