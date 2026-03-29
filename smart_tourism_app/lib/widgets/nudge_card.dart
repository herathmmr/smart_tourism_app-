import 'package:flutter/material.dart';
import '../models/destination.dart';
import '../core/constants.dart';

class NudgeCard extends StatelessWidget {
  final DestinationModel destination;

  const NudgeCard({super.key, required this.destination});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
      color: destination.isNudged ? Colors.teal.shade50 : Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (destination.isNudged)
              const Row(
                children: [
                  Icon(Icons.lightbulb, color: Colors.amber),
                  SizedBox(width: 8),
                  Text("Smart Alternative Found!",
                      style: TextStyle(
                          color: Colors.teal, fontWeight: FontWeight.bold)),
                ],
              ),
            const SizedBox(height: 10),
            Text(
              destination.name,
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              destination.description,
              style: const TextStyle(fontSize: 16, color: Colors.black87),
            ),
            const SizedBox(height: 15),
            Row(
              children: [
                Icon(
                  destination.crowdScore > 70
                      ? Icons.warning
                      : Icons.check_circle,
                  color: destination.crowdScore > 70
                      ? AppConstants.alertColor
                      : AppConstants.safeColor,
                ),
                const SizedBox(width: 8),
                Text(
                  destination.crowdStatus,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: destination.crowdScore > 70
                        ? AppConstants.alertColor
                        : AppConstants.safeColor,
                  ),
                ),
              ],
            )
          ],
        ),
      ),
    );
  }
}
