# Kafka Interview Q&A — Data Engineers (4 YOE)

> 28 questions covering architecture, replication, consumer groups, delivery semantics, performance tuning, and integration. Curated for engineers with ~4 years of experience.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Replication](#replication)
3. [Consumer Groups](#consumer-groups)
4. [Delivery Semantics](#delivery-semantics)
5. [Performance](#performance)
6. [Integration](#integration)

---

## Architecture

**Q1. What is the fundamental architecture of Apache Kafka and how does it differ from traditional message brokers?**

Kafka is a distributed, partitioned, replicated commit log service. Unlike traditional brokers like RabbitMQ that use a push-based model and delete messages after consumption, Kafka uses a pull-based model where data is persisted to disk for a configurable retention period. This allows multiple independent consumers to read the same stream at their own pace and replay historical data by seeking to older offsets.

---

**Q2. What are partitions and how do they enable horizontal scaling?**

Partitions are the unit of parallelism in Kafka. A topic is divided into multiple partitions distributed across brokers. Each partition can be hosted on a different server, so Kafka scales horizontally by adding brokers and increasing partition count. Different consumers in a consumer group can process different partitions simultaneously, allowing throughput that exceeds any single machine.

---

**Q3. Describe the transition from ZooKeeper to KRaft mode in Kafka.**

Historically, Kafka relied on Apache ZooKeeper for cluster coordination and metadata management. The KRaft (Kafka Raft) protocol incorporates metadata management directly into the Kafka brokers, removing the "split-brain" risks of managing two separate systems. This simplifies the architecture and allows Kafka clusters to scale to millions of partitions through a dedicated controller quorum within the cluster.

---

**Q4. What is the "zero-copy" optimization and how does it impact Kafka's performance?**

Zero-copy transfers data from the Linux Page Cache directly to the network socket without copying it into the application's user space, using the `sendfile()` system call. Kafka avoids multiple context switches between kernel and user mode, allowing near-line-rate network speeds while keeping CPU usage remarkably low.

---

**Q5. What is the role of the Controller broker in a Kafka cluster?**

The Controller is a single broker responsible for administrative tasks: partition leader election, topic creation/deletion, and replica management. If a broker fails, the Controller is notified and sends "LeaderAndIsr" requests to the remaining brokers to reassign leadership.

---

## Replication

**Q6. How does Kafka ensure message durability and high availability?**

Kafka ensures durability through a configurable replication factor. Each partition has one Leader and multiple Followers. All writes go through the Leader, while Followers replicate data. If a broker hosting a Leader fails, one of the In-Sync Replicas (ISRs) is automatically elected as the new leader. With `acks=all`, a message is not considered sent until all in-sync replicas acknowledge it.

---

**Q7. What are In-Sync Replicas (ISR) and why are they critical for data consistency?**

An ISR is a replica that is fully caught up with the leader's log within a specific time window. If a leader fails, Kafka only allows an ISR to become the new leader to prevent data loss. With "Unclean Leader Election" disabled, Kafka waits for an ISR rather than electing a "dirty" replica that might be missing data, prioritizing consistency over availability.

---

**Q8. What is "Unclean Leader Election" and when would you enable it?**

Unclean leader election allows a replica not in the ISR to become leader if all ISRs are unavailable. Enable it only when availability takes priority over durability — for example, non-critical real-time analytics. In financial systems it is strictly disabled to prevent data loss.

---

## Consumer Groups

**Q9. What is a Consumer Group Rebalance and what triggers it?**

A rebalance is when the Group Coordinator (a broker) redistributes partition ownership among consumer group members. It is triggered when:
- A consumer joins the group
- A consumer leaves or crashes
- Topic metadata changes (e.g., more partitions are added)

---

**Q10. What is the difference between Eager Rebalancing and Cooperative Sticky Rebalancing?**

| | Eager Rebalancing | Cooperative Sticky Rebalancing |
|---|---|---|
| **Behavior** | All consumers revoke all partitions before reassignment | Consumers keep current partitions; only the partitions that need to move are revoked |
| **Downtime** | Full processing stop during rebalance | Minimal — only affected partitions pause |
| **Use case** | Simpler but higher impact | Preferred for production workloads |

---

**Q11. What is the role of the Group Coordinator and the Group Leader?**

- **Group Coordinator**: A broker responsible for managing the state of a consumer group (membership, offsets).
- **Group Leader**: One consumer elected by the coordinator. During a rebalance, the coordinator provides the leader with a list of members, and the leader executes the partition assignment strategy.

---

**Q12. Explain the Partition Assignment Strategies available in Kafka.**

| Strategy | Behavior |
|---|---|
| `RangeAssignor` | Assigns contiguous ranges of partitions to each consumer |
| `RoundRobinAssignor` | Distributes partitions evenly across all consumers |
| `StickyAssignor` | Maximizes balance while minimizing partition movement during rebalances |

For new deployments, **Cooperative Sticky** is generally preferred.

---

**Q13. What is "Consumer Lag" and how do you monitor and remediate it?**

Consumer lag is the delta between the last produced offset and the last committed offset by a consumer.

**Monitoring**: JMX metrics, tools like Burrow, or Confluent Control Center.

**Remediation options**:
- Increase partition count to allow more consumers in the group
- Optimize consumer processing logic (reduce per-message work)
- Increase `fetch.max.bytes` to pull larger batches
- Scale consumers horizontally (up to the number of partitions)

---

## Delivery Semantics

**Q14. Explain the three message delivery semantics in Kafka.**

| Semantic | Guarantee | Risk | Config |
|---|---|---|---|
| At-most-once | Never redelivered | Message loss possible | `acks=0`, no retries |
| At-least-once | No data loss | Duplicates possible | `acks=all`, retries enabled |
| Exactly-once | No loss, no duplicates | Higher latency/complexity | Idempotent producer + Transactions |

---

**Q15. How do you implement Exactly-once Semantics (EOS) in a Kafka-to-Kafka pipeline?**

1. Enable `enable.idempotence=true` on the producer
2. Use the Transactional API (`initTransactions`, `beginTransaction`, `commitTransaction`)
3. The producer atomically commits output messages **and** consumer offsets together
4. If any part fails, the entire transaction rolls back

This ensures the output and offset commit happen together or not at all.

---

**Q16. What is the significance of the `acks` parameter in a Kafka producer?**

| Value | Behavior | Trade-off |
|---|---|---|
| `acks=0` | Producer fires and forgets | Highest speed, possible data loss |
| `acks=1` | Leader acknowledges write | Moderate guarantee |
| `acks=all` / `-1` | All ISRs acknowledge write | Strongest durability, higher latency |

---

**Q17. What is an Idempotent Producer and how does it prevent duplicates?**

An idempotent producer assigns a unique **Producer ID (PID)** and a monotonically increasing **sequence number** to every message batch. If a retry reaches the broker for a message it already received, the broker recognizes the duplicate via the PID + sequence number and discards it.

Enable with: `enable.idempotence=true`

---

**Q18. How can you ensure message ordering in a Kafka topic?**

- **Within a partition**: Ordering is always guaranteed.
- **Across all partitions**: Requires a single-partition topic (limits throughput).
- **Common pattern — Partial Ordering**: Route related messages using the **same key** so they land on the same partition, ensuring relative order for that entity (e.g., all events for `user_id=123` go to the same partition).

---

## Performance

**Q19. What are the pros and cons of batching in Kafka producers?**

| | Detail |
|---|---|
| **Pro** | Higher throughput, fewer network requests |
| **Con** | Increased latency — messages wait for `linger.ms` before being sent |
| **Key configs** | `linger.ms` (wait time), `batch.size` (max batch size in bytes) |

---

**Q20. Explain Producer Compression and which algorithms are supported.**

Compression reduces data size before sending. Applied at the batch level.

| Algorithm | CPU Usage | Compression Ratio | Best For |
|---|---|---|---|
| `gzip` | High | High | Archival, low-throughput |
| `snappy` | Low | Moderate | High-throughput pipelines |
| `lz4` | Very low | Moderate | Latency-sensitive workloads |
| `zstd` | Medium-High | Very high | Balanced compression+speed |

---

**Q21. What is Log Compaction and when is it used?**

Log compaction retains at least the **last known value for each message key** in the log, discarding older duplicates. Use cases:
- Maintaining the latest state of a record (e.g., user profile, account balance)
- Restoring state in stream processing applications
- Change Data Capture (CDC) topics acting as a database snapshot

Enable with: `cleanup.policy=compact`

---

**Q22. What are Tombstone messages in a log-compacted topic?**

A tombstone is a message with a **non-null key** and a **null value**. It signals that a record should be deleted. The log cleaner retains tombstones for `delete.retention.ms` before purging all records with that key, giving downstream consumers time to observe the deletion.

---

**Q23. How does Kafka handle backpressure without overwhelming consumers?**

Kafka's **pull-based model** is the built-in backpressure mechanism. Consumers request data from brokers only when they have capacity. If a consumer slows down, it simply makes fewer `poll()` calls. Data remains safely stored in the Kafka log until the retention period expires, acting as a durable, massive buffer — no explicit flow control protocol needed.

---

**Q24. What is "Jitter" and why should you use it in Kafka producers?**

Jitter adds a small **random delay** to retry intervals. Without it, many producers attempting to reconnect simultaneously after a broker failure create a "thundering herd" effect that can overwhelm a recovering broker. Jitter spreads reconnect attempts over time, allowing the cluster to recover gracefully.

---

## Integration

**Q25. What is the purpose of the Kafka Schema Registry?**

The Schema Registry provides a centralized repository for managing and versioning schemas (Avro, JSON Schema, Protobuf). Producers register schemas and include only a **schema ID** in each message; consumers look up the schema at read time. Benefits:
- Prevents "poison pill" messages by enforcing compatibility rules
- Reduces message size (no full schema embedded per message)
- Supports backward/forward/full compatibility modes

---

**Q26. How would you design a Kafka-based CDC (Change Data Capture) pipeline?**

```
Database → Debezium (Kafka Connect Source) → Kafka Topics → Stream Processor / Sink
```

1. Deploy **Debezium** as a Kafka Connect source connector — streams row-level changes from the source DB (PostgreSQL, MySQL, etc.) into Kafka topics (one topic per table)
2. Use a **Schema Registry** (Avro) for schema management
3. Enable **log compaction** on CDC topics to maintain a full table snapshot
4. Downstream consumers (Spark, Flink, Kafka Connect Sink) process or forward events

---

**Q27. What is Kafka Connect and how does it differ from writing a custom producer/consumer?**

| | Kafka Connect | Custom Producer/Consumer |
|---|---|---|
| **Offset management** | Built-in, automatic | Must implement manually |
| **Fault tolerance** | Handles restarts, retries | Must implement manually |
| **Scaling** | Declarative (tasks config) | Manual scaling logic |
| **Reuse** | 200+ pre-built connectors | Bespoke per use case |
| **Best for** | Standard integrations (DB, S3, Elasticsearch) | Complex custom logic |

---

**Q28. How does Kafka integrate with Apache Spark or Flink for stream processing?**

**Apache Spark Structured Streaming**:
- Uses the built-in Kafka source (`readStream.format("kafka")`)
- Tracks offsets in checkpoints for exactly-once processing
- Triggers can be micro-batch or continuous

**Apache Flink**:
- Uses the native `KafkaSource` / `KafkaSink` connectors
- Manages offsets via its state backend
- Enables exactly-once semantics through checkpointing + Kafka transactions

Both treat Kafka as a **durable, replayable source of truth**, decoupling ingestion from processing.

---

## Quick Reference Cheat Sheet

| Config | Purpose | Recommended Value |
|---|---|---|
| `acks` | Durability guarantee | `all` for production |
| `enable.idempotence` | Prevent duplicate messages | `true` |
| `linger.ms` | Batching wait time | 5–20ms for throughput |
| `compression.type` | Network efficiency | `snappy` or `zstd` |
| `fetch.max.bytes` | Consumer batch size | Tune based on lag |
| `max.poll.records` | Records per poll | 500 (default), tune down if processing is slow |
| `cleanup.policy` | Retention strategy | `delete` (default) or `compact` |
| `replication.factor` | Fault tolerance | 3 for production |
| `min.insync.replicas` | Minimum ISRs for write | 2 for production |

---

*Sources: DataVidhya, DataCamp, GeeksforGeeks, Terminal.io — compiled June 2026*
