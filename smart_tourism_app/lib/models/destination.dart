class DestinationModel {
  final String name;
  final String description;
  final String crowdStatus;
  final int crowdScore;
  final bool isNudged;
  DestinationModel({
    required this.name,
    required this.description,
    required this.crowdStatus,
    required this.crowdScore,
    required this.isNudged,
  });

  factory DestinationModel.fromJson(Map<String, dynamic> json) {
    return DestinationModel(
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      crowdStatus: json['crowd_status'] ?? '',
      crowdScore: json['crowd_score'] ?? 0,
      isNudged: json['is_nudged'] ?? false,
    );
  }
}
