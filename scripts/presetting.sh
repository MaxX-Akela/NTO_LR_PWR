#!/bin/bash


echo aruco.launch Настроен

sed -i '3s|<arg name="aruco_map" default="false"/>|<arg name="aruco_map" default="true"/>|' aruco.launch
sed -i '4s|<arg name="aruco_vpe" default="false"/>|<arg name="aruco_vpe" default="true"/>|' aruco.launch
sed -i '7s|<arg name="map" default="map.txt"/>|<arg name="map" default="cmit.txt"/>|' aruco.launch

echo clover.launch Настроен

sed -i '10s|<arg name="aruco" default="false"/>|<arg name="aruco" default="true"/>|' clover.launch

dir="$(rospack find clover_simulation)/resources/worlds"
worlds=("$dir"/*.world)

random_world=${worlds[$random % ${#worlds[@]}]}
name=$(name "$random_world")

SIM_LAUNCH=$(rospack find clover_simulation)/launch/simulator.launch


echo simulator.launch Настроен

sed -i "s|<arg name=\"world_name\" value=\".*\"/>|<arg name=\"world_name\" value=\"$(rospack find clover_simulation)/resources/worlds/$name\"/>|" "$SIM_LAUNCH"
