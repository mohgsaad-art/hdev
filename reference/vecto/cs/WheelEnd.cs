using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Models.Connector.Ports;
using TUGraz.VectoCore.Models.Simulation;
using TUGraz.VectoCore.Models.Simulation.Data;
using TUGraz.VectoCore.Models.SimulationComponent.Data;
using TUGraz.VectoCore.OutputData;
using TUGraz.VectoCore.Configuration;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
    public class WheelEnd : 
        StatefulVectoSimulationComponent<SimpleComponentState>, IWheelEnd, ITnInPort, ITnOutPort, IUpdateable
    {
        protected ITnOutPort _nextComponent;
        protected NewtonMeter _deltaFrictionTorque;
        
        public WheelEnd(IVehicleContainer container, WheelEndData modelData) : base(container, Constants.NOT_IN_AXLE_POWERTRAIN)
        { 
            _deltaFrictionTorque = modelData?.DeltaFrictionTorque ?? 0.SI<NewtonMeter>();
        }

        public IResponse Request(Second absTime, Second dt, NewtonMeter outTorque, PerSecond outAngularVelocity, 
            bool dryRun)
        {
            CurrentState.SetState(outTorque + _deltaFrictionTorque, outAngularVelocity, outTorque, outAngularVelocity); 
            
            return _nextComponent.Request(absTime, dt, outTorque + _deltaFrictionTorque, outAngularVelocity, dryRun);
        }

        public virtual void Connect(ITnOutPort other)
		{
			_nextComponent = other;
		}

        public virtual ITnInPort InPort()
		{
			return this;
		}

		public virtual ITnOutPort OutPort()
		{
			return this;
        }

        public virtual IResponse Initialize(NewtonMeter outTorque, PerSecond outAngularVelocity)
        { 
            PreviousState.SetState(outTorque, outAngularVelocity, outTorque, outAngularVelocity);

            return _nextComponent.Initialize(outTorque, outAngularVelocity);
        }

        protected override void DoCommitSimulationStep(Second time, Second simulationInterval)
        {
            AdvanceState();
        }

        protected override void DoWriteModalResults(Second time, Second simulationInterval, IModalDataContainer container)
        { 
            container[ModalResultField.P_wheelEnd_saving] = 
                _deltaFrictionTorque * (PreviousState.InAngularVelocity + CurrentState.InAngularVelocity) / 2.0;

			container[ModalResultField.P_wheelEnd_in] = CurrentState.InTorque *
													(PreviousState.InAngularVelocity + CurrentState.InAngularVelocity) / 2.0;
		}

        protected override bool DoUpdateFrom(object other) 
        {
			if (other is WheelEnd w) {
				PreviousState = w.PreviousState.Clone();
				return true;
			}

			return false;
		}

    }
}
