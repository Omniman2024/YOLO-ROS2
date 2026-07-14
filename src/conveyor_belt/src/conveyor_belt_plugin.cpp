#include "conveyor_belt/conveyor_belt_plugin.hpp"

#include <memory>
#include <string>
#include <vector>

#include <gz/common/Console.hh>
#include <gz/plugin/Register.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/components/JointPosition.hh>
#include <gz/sim/components/JointPositionReset.hh>

namespace conveyor_belt
{

class ConveyorBeltPluginPrivate
{
  public: gz::sim::Model model;
  public: gz::sim::Entity jointEntity{gz::sim::kNullEntity};
  public: std::string jointName{"belt_joint"};
  public: double lowerLimit{0.0};
  public: double upperLimit{0.01};
  public: double resetEpsilon{5e-4};
};

ConveyorBeltPlugin::ConveyorBeltPlugin()
: dataPtr(std::make_unique<ConveyorBeltPluginPrivate>())
{
}

ConveyorBeltPlugin::~ConveyorBeltPlugin() = default;

void ConveyorBeltPlugin::Configure(
    const gz::sim::Entity &_entity,
    const std::shared_ptr<const sdf::Element> &_sdf,
    gz::sim::EntityComponentManager &_ecm,
    gz::sim::EventManager &)
{
  this->dataPtr->model = gz::sim::Model(_entity);

  if (!this->dataPtr->model.Valid(_ecm))
  {
    gzerr << "ConveyorBeltPlugin must be attached to a model entity.\n";
    return;
  }

  if (_sdf && _sdf->HasElement("joint_name"))
  {
    this->dataPtr->jointName = _sdf->Get<std::string>("joint_name");
  }

  if (_sdf && _sdf->HasElement("lower_limit"))
  {
    this->dataPtr->lowerLimit = _sdf->Get<double>("lower_limit");
  }

  if (_sdf && _sdf->HasElement("upper_limit"))
  {
    this->dataPtr->upperLimit = _sdf->Get<double>("upper_limit");
  }

  if (_sdf && _sdf->HasElement("reset_epsilon"))
  {
    this->dataPtr->resetEpsilon = _sdf->Get<double>("reset_epsilon");
  }

  this->dataPtr->jointEntity =
      this->dataPtr->model.JointByName(_ecm, this->dataPtr->jointName);

  if (this->dataPtr->jointEntity == gz::sim::kNullEntity)
  {
    gzerr << "Failed to find joint [" << this->dataPtr->jointName
          << "] for ConveyorBeltPlugin.\n";
    return;
  }

  _ecm.ComponentDefault<gz::sim::components::JointPosition>(
      this->dataPtr->jointEntity, std::vector<double>{});
}

void ConveyorBeltPlugin::PreUpdate(
    const gz::sim::UpdateInfo &_info,
    gz::sim::EntityComponentManager &_ecm)
{
  if (_info.paused || this->dataPtr->jointEntity == gz::sim::kNullEntity)
  {
    return;
  }

  const auto *jointPosition =
      _ecm.Component<gz::sim::components::JointPosition>(
          this->dataPtr->jointEntity);

  if (jointPosition == nullptr || jointPosition->Data().empty())
  {
    return;
  }

  const double threshold =
      this->dataPtr->upperLimit - this->dataPtr->resetEpsilon;

  if (jointPosition->Data().front() < threshold)
  {
    return;
  }

  _ecm.SetComponentData<gz::sim::components::JointPositionReset>(
      this->dataPtr->jointEntity, std::vector<double>{this->dataPtr->lowerLimit});
}

}  // namespace conveyor_belt

GZ_ADD_PLUGIN(
    conveyor_belt::ConveyorBeltPlugin,
    gz::sim::System,
    gz::sim::ISystemConfigure,
    gz::sim::ISystemPreUpdate)

GZ_ADD_PLUGIN_ALIAS(
    conveyor_belt::ConveyorBeltPlugin,
    "conveyor_belt::ConveyorBeltPlugin")
