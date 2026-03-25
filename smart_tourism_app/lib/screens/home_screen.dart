import 'package:flutter/material.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _noiseStatus = "Mic not active";

  // වෙනම function එකක් විදියට ලියන එක professional
  void _analyzeSerenity() {
    setState(() {
      _noiseStatus = "Recording Noise Level... (Simulating)";
    });
    // පස්සේ අපි මෙතනින් services ෆෝල්ඩර් එකේ තියෙන Audio Service එකට කතා කරනවා
  }

  @override
  void dispose() {
    _searchController.dispose(); // Memory leaks නවත්තන්න
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Travel Analyzer & Nudging'),
        centerTitle: true,
        elevation: 0,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Where do you want to go?',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 30),
              TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  labelText: 'Enter Destination (e.g. Ella)',
                  prefixIcon: const Icon(Icons.search),
                ),
              ),
              const SizedBox(height: 40),
              ElevatedButton.icon(
                onPressed: _analyzeSerenity,
                icon: const Icon(Icons.mic, size: 24),
                label: const Padding(
                  padding: EdgeInsets.symmetric(vertical: 16.0),
                  child: Text('Analyze Crowd & Serenity',
                      style: TextStyle(fontSize: 18)),
                ),
                style: ElevatedButton.styleFrom(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Text(
                _noiseStatus,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: Colors.blueGrey,
                  fontSize: 16,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
