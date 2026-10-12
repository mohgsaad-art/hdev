using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Models.Simulation;
using TUGraz.VectoCore.Models.Simulation.Data;
using TUGraz.VectoCore.Configuration;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
    public class BEVCycleGearbox : CycleGearbox
    {
        public BEVCycleGearbox(IVehicleContainer container, VectoRunData runData, int axleNumber) : 
            base(container, axleNumber)
        {}

        protected override IResponse GetDisengagedResponse(Second absTime, Second dt, PerSecond outAngularVelocity)
        {
            /* In BEVs there is no ICE engine, so it is necessary to have an implementation of this method that does not 
             * invoke the method CycleGearbox:EngineIdleRequest, as CycleGearbox:GetDisengagedResponse does.
             */

            var outVelocity = outAngularVelocity * ((NextGear.Gear > 0) ? ModelData.Gears[NextGear.Gear].Ratio : 1);
            
            return NextComponent.Request(absTime, dt, 0.SI<NewtonMeter>(), outVelocity, false);
        }
    }
}
