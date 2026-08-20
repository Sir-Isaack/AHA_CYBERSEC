#!/bin/bash

echo "Enter your weight in kgs"
read weight
echo "Enter your height in metres"
read height

bmi=$(echo "scale=2; $weight / ($height * $height)" | bc)

echo "Your BMI is $bmi"
