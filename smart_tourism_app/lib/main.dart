import 'package:flutter/material.dart';
import 'screens/home_screen.dart'; // අලුත් ෆෝල්ඩර් එකෙන් import කරගන්නවා

void main() {
  runApp(const SmartTourismApp());
}

class SmartTourismApp extends StatelessWidget {
  const SmartTourismApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Tourism Nudging',
      theme: ThemeData(
        primarySwatch: Colors.teal,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: const HomeScreen(), // Home Screen එකට යවනවා
      debugShowCheckedModeBanner: false,
    );
  }
}
