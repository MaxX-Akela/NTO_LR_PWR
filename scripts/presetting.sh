#!/bin/bash


echo aruco.launch
sed -i '3s|<arg name="aruco_map" default="false"/>|<arg name="aruco_map" default="true"/>|' aruco.launch
sed -i '4s|<arg name="aruco_vpe" default="false"/>|<arg name="aruco_vpe" default="true"/>|' aruco.launch
sed -i '7s|<arg name="map" default="map.txt"/>|<arg name="map" default="cmit.txt"/>|' aruco.launch

echo clover.launch
sed -i '10s|<arg name="aruco" default="false"/>|<arg name="aruco" default="true"/>|' clover.launch