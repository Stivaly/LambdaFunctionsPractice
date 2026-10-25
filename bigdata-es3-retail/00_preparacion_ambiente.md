# Preparación del ambiente (antes de grabar)

Zorin OS (base Ubuntu) + **OpenJDK 8**. Esta parte no se graba completa; solo se muestran `jps` y las versiones en el video.

## 1. Java 8 como versión activa

```bash
sudo apt install openjdk-8-jdk                # si no está
sudo update-alternatives --config java        # elegir la ruta .../java-8-openjdk-amd64/...
sudo update-alternatives --config javac
java -version                                 # debe decir 1.8.0_xxx
```

## 2. Variables de entorno (`~/.bashrc`)

Ajusta las rutas a donde descomprimiste cada herramienta.

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=$HOME/bigdata/hadoop-3.3.6
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export PIG_HOME=$HOME/bigdata/pig-0.17.0
export HIVE_HOME=$HOME/bigdata/apache-hive-3.1.3-bin
export HBASE_HOME=$HOME/bigdata/hbase-2.5.10
export MAHOUT_HOME=$HOME/bigdata/apache-mahout-distribution-0.13.0
export PIG_CLASSPATH=$HADOOP_CONF_DIR
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PIG_HOME/bin:$HIVE_HOME/bin:$HBASE_HOME/bin:$MAHOUT_HOME/bin
```

```bash
source ~/.bashrc
```

También fija `JAVA_HOME` en `$HADOOP_HOME/etc/hadoop/hadoop-env.sh` y en `$HBASE_HOME/conf/hbase-env.sh` (los daemons no leen `.bashrc`).

## 3. Configuración mínima (pseudo-distribuido, una máquina)

`$HADOOP_HOME/etc/hadoop/core-site.xml`
```xml
<configuration>
  <property><name>fs.defaultFS</name><value>hdfs://localhost:9000</value></property>
</configuration>
```

`$HADOOP_HOME/etc/hadoop/hdfs-site.xml`
```xml
<configuration>
  <property><name>dfs.replication</name><value>1</value></property>
  <property><name>dfs.namenode.name.dir</name><value>file:///home/TU_USUARIO/hadoop_data/namenode</value></property>
  <property><name>dfs.datanode.data.dir</name><value>file:///home/TU_USUARIO/hadoop_data/datanode</value></property>
</configuration>
```

`$HADOOP_HOME/etc/hadoop/mapred-site.xml`
```xml
<configuration>
  <property><name>mapreduce.framework.name</name><value>yarn</value></property>
  <property><name>mapreduce.application.classpath</name>
    <value>$HADOOP_HOME/share/hadoop/mapreduce/*:$HADOOP_HOME/share/hadoop/mapreduce/lib/*</value></property>
  <property><name>yarn.app.mapreduce.am.env</name><value>HADOOP_MAPRED_HOME=${HADOOP_HOME}</value></property>
  <property><name>mapreduce.map.env</name><value>HADOOP_MAPRED_HOME=${HADOOP_HOME}</value></property>
  <property><name>mapreduce.reduce.env</name><value>HADOOP_MAPRED_HOME=${HADOOP_HOME}</value></property>
</configuration>
```

`$HADOOP_HOME/etc/hadoop/yarn-site.xml`
```xml
<configuration>
  <property><name>yarn.nodemanager.aux-services</name><value>mapreduce_shuffle</value></property>
</configuration>
```

`$HBASE_HOME/conf/hbase-site.xml` (HBase guardando en HDFS, para poder mostrar su ruta física)
```xml
<configuration>
  <property><name>hbase.cluster.distributed</name><value>true</value></property>
  <property><name>hbase.rootdir</name><value>hdfs://localhost:9000/hbase</value></property>
  <property><name>hbase.zookeeper.property.dataDir</name><value>/home/TU_USUARIO/hadoop_data/zookeeper</value></property>
  <property><name>hbase.unsafe.stream.capability.enforce</name><value>false</value></property>
</configuration>
```

> Si tu HBase ya funciona en modo standalone con disco local, sirve igual; en ese caso en el video muestras la ruta local de `hbase.rootdir` en vez de `/hbase` en HDFS.

## 4. Primer arranque (solo una vez)

```bash
hdfs namenode -format                                  # SOLO la primera vez: borra HDFS
schematool -dbType derby -initSchema                   # metastore de Hive (ejecutar dentro de ~/retail_es3)
```

> Con Derby embebido, el metastore (`metastore_db/`) se crea en el directorio desde donde ejecutas `hive`. **Ejecuta siempre `hive` desde `~/retail_es3`**, o perderás las tablas.

## 5. Arranque antes de cada sesión de grabación

```bash
start-dfs.sh
start-yarn.sh
mapred --daemon start historyserver      # Pig lo usa para leer contadores de jobs
start-hbase.sh
jps
```

`jps` debe mostrar: `NameNode`, `DataNode`, `SecondaryNameNode`, `ResourceManager`, `NodeManager`, `JobHistoryServer`, `HMaster`, `HRegionServer`, `HQuorumPeer` (este último solo si HBase gestiona su ZooKeeper).

Interfaces web útiles (para mostrar si sobra tiempo): NameNode `http://localhost:9870`, YARN `http://localhost:8088`, HBase `http://localhost:16010`.

## 6. Verificación de versiones (se muestra en el video)

```bash
java -version
hadoop version | head -1
pig -version
hive --version | head -1
hbase version 2>/dev/null | head -1
ls $MAHOUT_HOME/*.jar
```

## 7. Reinicio limpio (para grabar el flujo desde cero)

```bash
hdfs dfs -rm -r -f /retail
hive -e "DROP DATABASE IF EXISTS retail_dw CASCADE;"
echo "disable 'perfiles_cliente'; drop 'perfiles_cliente'" | hbase shell -n 2>/dev/null
```

## 8. Carpeta de trabajo

```bash
mkdir -p ~/retail_es3/{datos,scripts,resultados}
cd ~/retail_es3/datos
unzip ~/Descargas/ES3_BigData_Datos_Retail.zip
ls -l
```
