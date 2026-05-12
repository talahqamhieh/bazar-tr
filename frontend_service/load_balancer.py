class RoundRobin:
    def __init__(self, replicas, label_prefix):
        self.replicas = replicas
        self.label_prefix = label_prefix
        self.index = 0

    def next_replica(self):
        position = self.index % len(self.replicas)
        self.index += 1
        return f"{self.label_prefix}_{position + 1}", self.replicas[position]
