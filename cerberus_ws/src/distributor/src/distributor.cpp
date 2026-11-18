#include <memory>
#include <chrono>
#include "settings.h"

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joy.hpp"
#include "map.h"

#define TIMEOUT 10.0

class Stopwatch
{
public:
  void start()
  {
    start_time = std::chrono::high_resolution_clock::now();
  }
  double elapsedMilliseconds()
  {
    auto now = std::chrono::high_resolution_clock::now();
    return std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time).count();
  }
  void reset()
  {
    start_time = std::chrono::high_resolution_clock::now();
  }

private:
  std::chrono::time_point<std::chrono::high_resolution_clock> start_time;
};

using std::placeholders::_1;
class Distributor : public rclcpp::Node
{
public:
  Distributor()
      : Node("Distributor_node") // name of the node
  {
    joy_subscriber = this->create_subscription<sensor_msgs::msg::Joy>( // Creating the subscriber to the Joy topic
        "/joy", 10, std::bind(&Distributor::joy_callback, this, _1));

    timer_ = this->create_wall_timer(
        std::chrono::milliseconds(500),
        std::bind(&Distributor::timer_callback, this)); // Timer for tasks we want to run on a loop of some sort

    stopwatch.start();
    RCLCPP_INFO(this->get_logger(), "DISTRIBUTOR ONLINE");
  }

private:
  void joy_callback(sensor_msgs::msg::Joy::SharedPtr msg)
  {

  }

  void timer_callback()
  {

  }
  // this is where you can declare subscribers/publishers.
  rclcpp::Subscription<sensor_msgs::msg::Joy>::SharedPtr joy_subscriber;
  rclcpp::TimerBase::SharedPtr timer_;
  // rclcpp::Timer timer_
};

int main(int argc, char *argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Distributor>());
  rclcpp::shutdown();
  return 0;
}