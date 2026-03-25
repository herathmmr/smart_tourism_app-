import 'dart:async';
import 'dart:math';

class AudioSensorService {
  Future<double> getCurrentNoiseLevel() async {
    await Future.delayed(const Duration(seconds: 3));

    Random random = Random();
    double simulatedDb = 60 + random.nextInt(35).toDouble();

    return simulatedDb;
  }
}
