import org.apache.hadoop.conf.Configuration;
  import org.apache.hadoop.hbase.*;
  import org.apache.hadoop.hbase.client.*;

  public class AtomicOperation {
      public static void main(String[] args) throws Exception {
          Configuration conf = HBaseConfiguration.create();
          conf.set("hbase.zookeeper.quorum", "hbase-homework");
          conf.set("hbase.zookeeper.property.clientPort", "2181");

          Connection connection = ConnectionFactory.createConnection(conf);
          Table table = connection.getTable(TableName.valueOf("car_sales"));

          byte[] rowKey = "北京_20240315_C1001".getBytes();
          byte[] family = "info".getBytes();
          byte[] qualifier = "status".getBytes();

          // 第一步：先把状态设为 pending
          Put put = new Put(rowKey);
          put.addColumn(family, qualifier, "pending".getBytes());
          table.put(put);
          System.out.println("当前状态已设为 pending");

          // 第二步：成功场景 - 当前是 pending，改成 sold
          boolean success = table.checkAndMutate(rowKey, family)
              .qualifier(qualifier)
              .ifEqual("pending".getBytes())
              .thenPut(new Put(rowKey).addColumn(family, qualifier, "sold".getBytes()));
          System.out.println("成功场景（pending->sold）：" + success);

          // 第三步：失败场景 - 当前是 sold，尝试再改成 pending
          boolean fail = table.checkAndMutate(rowKey, family)
              .qualifier(qualifier)
              .ifEqual("pending".getBytes())
              .thenPut(new Put(rowKey).addColumn(family, qualifier, "pending".getBytes()));
          System.out.println("失败场景（sold->pending）：" + fail);

          // 第四步：验证最终状态
          Get get = new Get(rowKey);
          get.addColumn(family, qualifier);
          Result result = table.get(get);
          String finalStatus = new String(result.getValue(family, qualifier));
          System.out.println("最终状态：" + finalStatus);

          table.close();
          connection.close();
      }
  }