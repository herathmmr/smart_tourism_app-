import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants.dart';
import '../models/destination.dart';

class ApiService {
  Future<DestinationModel?> getRecommendation(
      String location, double noiseLevel) async {
    try {
      /* final response = await http.post(
        Uri.parse(AppConstants.backendUrl),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "location": location,
          "noise_db": noiseLevel,
        }),
      );

      if (response.statusCode == 200) {
        return DestinationModel.fromJson(jsonDecode(response.body));
      }
      */

      await Future.delayed(const Duration(seconds: 2));
      return DestinationModel(
        name: "Little Adam's Peak",
        description: "A serene and quiet alternative with a beautiful view.",
        crowdStatus: "Low Crowd (Serene)",
        crowdScore: 25,
        isNudged: true,
      );
    } catch (e) {
      print("API Error: $e");
      return null;
    }
  }
}
