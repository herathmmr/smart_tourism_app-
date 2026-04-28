import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const SmartTourismApp());
}

class SmartTourismApp extends StatelessWidget {
  const SmartTourismApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Tourism',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2E7D32), // Nature green
          primary: const Color(0xFF2E7D32),
          secondary: const Color(0xFF8D6E63), // Earthy brown
          background: const Color(0xFFF1F8E9), // Light green-white
          surface: Colors.white,
        ),
        textTheme: GoogleFonts.poppinsTextTheme(
          Theme.of(context).textTheme,
        ),
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          elevation: 0,
          backgroundColor: Colors.transparent,
          iconTheme: IconThemeData(color: Colors.black87),
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
