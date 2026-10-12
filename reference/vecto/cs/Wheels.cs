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

using TUGraz.VectoCommon.Models;
using TUGraz.VectoCommon.Utils;
using TUGraz.VectoCore.Models.Connector.Ports;
using TUGraz.VectoCore.Models.Simulation;
using TUGraz.VectoCore.Models.Simulation.Data;
using TUGraz.VectoCore.OutputData;
using TUGraz.VectoCore.Utils;
using TUGraz.VectoCore.Configuration;

namespace TUGraz.VectoCore.Models.SimulationComponent.Impl
{
    public class Wheels : StatefulProviderComponent<Wheels.WheelsState, IFvOutPort, ITnInPort, ITnOutPort>, IWheels,
		IFvOutPort, ITnInPort, IUpdateable
	{
		private readonly KilogramSquareMeter _totalWheelsInertia;

		public class WheelsState
		{
			public PerSecond AngularVelocity;
			public NewtonMeter TorqueIn;
			public NewtonMeter InertiaTorqueLoss;

			public WheelsState Clone() => (WheelsState)MemberwiseClone();
		}

		public Wheels(IVehicleContainer container, Meter rdyn, KilogramSquareMeter totalWheelsInertia)
			: base(container, Constants.NOT_IN_AXLE_POWERTRAIN)
		{
			DynamicTyreRadius = rdyn;
			_totalWheelsInertia = totalWheelsInertia;
		}

		public IResponse Initialize(Newton force, MeterPerSecond velocity)
		{
			PreviousState.TorqueIn = force * DynamicTyreRadius;
			PreviousState.AngularVelocity = velocity / DynamicTyreRadius;
			PreviousState.InertiaTorqueLoss = 0.SI<NewtonMeter>();

			return NextComponent.Initialize(PreviousState.TorqueIn, PreviousState.AngularVelocity);
		}

		public IResponse Request(Second absTime, Second dt, Newton force, MeterPerSecond velocity, bool dryRun)
		{
			Log.Debug("request: force: {0}, velocity: {1}", force, velocity);

			CurrentState.AngularVelocity = velocity / DynamicTyreRadius;
			var avgAngularSpeed = (CurrentState.AngularVelocity + PreviousState.AngularVelocity) / 2.0;
			CurrentState.InertiaTorqueLoss = avgAngularSpeed.IsEqual(0.SI<PerSecond>())
				? 0.SI<NewtonMeter>()
				: Formulas.InertiaPower(CurrentState.AngularVelocity, PreviousState.AngularVelocity, _totalWheelsInertia, dt) /
				avgAngularSpeed; //(_totalWheelsInertia * avgAngularSpeed / dt).Cast<NewtonMeter>();
			CurrentState.TorqueIn = force * DynamicTyreRadius + CurrentState.InertiaTorqueLoss;
			var retVal = NextComponent.Request(absTime, dt, CurrentState.TorqueIn, CurrentState.AngularVelocity,
				dryRun);

			retVal.Wheels.PowerRequest = CurrentState.TorqueIn * avgAngularSpeed;
			return retVal;
		}

		protected override void DoWriteModalResults(Second time, Second simulationInterval, IModalDataContainer container)
		{
			var avgAngularSpeed = (CurrentState.AngularVelocity + PreviousState.AngularVelocity) / 2.0;

			container[ModalResultField.P_wheel_in] = CurrentState.TorqueIn * avgAngularSpeed;
			container[ModalResultField.P_wheel_inertia] = CurrentState.InertiaTorqueLoss * avgAngularSpeed;
		}

		public Kilogram ReducedMassWheels => (_totalWheelsInertia / DynamicTyreRadius / DynamicTyreRadius).Cast<Kilogram>();

		public Meter DynamicTyreRadius { get; }

		#region Implementation of IUpdateable

		protected override bool DoUpdateFrom(object other) {
			if (other is Wheels w) {
				PreviousState = w.PreviousState.Clone();
				return true;
			}
			return false;
		}

		#endregion
	}
}