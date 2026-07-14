#ifndef CONVEYOR_BELT__CONVEYOR_BELT_PLUGIN_HPP_
#define CONVEYOR_BELT__CONVEYOR_BELT_PLUGIN_HPP_

#include <memory>

#include <gz/sim/System.hh>

namespace conveyor_belt
{

class ConveyorBeltPluginPrivate;

class ConveyorBeltPlugin
    : public gz::sim::System,
      public gz::sim::ISystemConfigure,
      public gz::sim::ISystemPreUpdate
{
  public: ConveyorBeltPlugin();

  public: ~ConveyorBeltPlugin() override;

  public: void Configure(
      const gz::sim::Entity &_entity,
      const std::shared_ptr<const sdf::Element> &_sdf,
      gz::sim::EntityComponentManager &_ecm,
      gz::sim::EventManager &_eventMgr) override;

  public: void PreUpdate(
      const gz::sim::UpdateInfo &_info,
      gz::sim::EntityComponentManager &_ecm) override;

  private: std::unique_ptr<ConveyorBeltPluginPrivate> dataPtr;
};

}  // namespace conveyor_belt

#endif  // CONVEYOR_BELT__CONVEYOR_BELT_PLUGIN_HPP_
