import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:async';

class DestinationDetailScreen extends StatefulWidget {
  final String name;
  final String imageUrl;
  final String description;

  const DestinationDetailScreen({
    super.key,
    required this.name,
    required this.imageUrl,
    required this.description,
  });

  @override
  State<DestinationDetailScreen> createState() => _DestinationDetailScreenState();
}

class _DestinationDetailScreenState extends State<DestinationDetailScreen> {
  bool _isLoading = false;
  bool _showResult = false;
  int _crowdDensity = 0;
  final ImagePicker _picker = ImagePicker();

  Future<void> uploadImageToBackend() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.camera);
    if (image != null) {
      _simulateSensingAndNudging();
    }
  }

  Future<void> sendAudioToBackend() async {
    // Simulating recording ambient noise
    _simulateSensingAndNudging();
  }

  void _simulateSensingAndNudging() {
    setState(() {
      _isLoading = true;
      _showResult = false;
    });

    // Simulate network delay
    Timer(const Duration(seconds: 3), () {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _showResult = true;
          _crowdDensity = 120; // Simulate a high crowd density
        });
      }
    });
  }

  void _showSensingOptions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Live Crowd Sensing',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: () {
                  Navigator.pop(context);
                  uploadImageToBackend();
                },
                icon: const Icon(Icons.camera_alt),
                label: const Text('Capture Image (Visual)'),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 50),
                ),
              ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: () {
                  Navigator.pop(context);
                  sendAudioToBackend();
                },
                icon: const Icon(Icons.mic),
                label: const Text('Record Noise (Acoustic)'),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 50),
                ),
              ),
              const SizedBox(height: 16),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 300,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              background: Image.network(
                widget.imageUrl,
                fit: BoxFit.cover,
                color: Colors.black.withOpacity(0.3),
                colorBlendMode: BlendMode.darken,
              ),
              title: Text(widget.name),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'About',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    widget.description,
                    style: TextStyle(color: Colors.grey.shade700, height: 1.5),
                  ),
                  const SizedBox(height: 32),
                  Center(
                    child: ElevatedButton(
                      onPressed: _showSensingOptions,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(30),
                        ),
                      ),
                      child: const Text(
                        'Check Live Crowd Density',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  if (_isLoading)
                    const Center(
                      child: Column(
                        children: [
                          CircularProgressIndicator(),
                          SizedBox(height: 16),
                          Text('Analyzing crowd density...'),
                        ],
                      ),
                    ),
                  if (_showResult) ...[
                    // Crowd Density Card
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.05),
                            blurRadius: 10,
                          ),
                        ],
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.people, size: 40, color: Colors.orange),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Crowd Density Score',
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                Text(
                                  _crowdDensity > 100 ? 'HIGH ($_crowdDensity persons)' : 'LOW ($_crowdDensity persons)',
                                  style: TextStyle(
                                    color: _crowdDensity > 100 ? Colors.red : Colors.green,
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    // Algorithmic Nudge Card (Shown if crowd is high)
                    if (_crowdDensity > 100)
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFFF9C4), // Soft yellow/earthy background
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: Colors.orange.shade200),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.lightbulb, color: Colors.orange.shade800),
                                const SizedBox(width: 8),
                                Text(
                                  'Algorithmic Nudge',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.orange.shade900,
                                    fontSize: 16,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            Text(
                              'It looks very crowded here! How about visiting Pidurangala Rock, a peaceful alternative just 10 mins away?',
                              style: TextStyle(color: Colors.orange.shade900),
                            ),
                            const SizedBox(height: 16),
                            Align(
                              alignment: Alignment.centerRight,
                              child: ElevatedButton(
                                onPressed: () {
                                  // Navigate to alternative micro-destination
                                },
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.orange.shade50,
                                  foregroundColor: Colors.orange.shade900,
                                  elevation: 0,
                                ),
                                child: const Text('Take me there'),
                              ),
                            ),
                          ],
                        ),
                      ),
                  ]
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
