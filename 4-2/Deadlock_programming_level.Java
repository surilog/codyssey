public class Main {
    public static void main(String[]args){
        Object lock1= new Object();
        Object lock2 = new Object();

        Thread t1 = new Thread(() -> {...});
        Thread t2 = new Thread(() -> {...});

        t1.start();
        t2.start();
    }
}

Thread t1 = new Thread(() -> {
    synchronized (lock1){
        System.out.println("[t1] get lock1");
        synchronized(lock2){
            System.out.println("[t2] get lock2");
        }
    }
})


Thread t2 = new Thread(() -> {
    synchronized (lock2){
        System.out.println("[t2] get lock1");
        synchronized(lock1){
            System.out.println("[t1] get lock2");
        }
    }
})


// 해겳 방법
//1. 개발 시 상호 배제가 반드시 필요한 건지 확인!
//2. 상호 배제가 필요한 상황이면 Thread t2에서도 lock1을 먼저 취득하게 만들고 
// 그 후에 lock2를 취득하게 만들어서 순환대기가 생기지 않기 때문에 deadlock 벗어남
// 3. 현재 중첩 (Thread 1에서는 lock1을 취득하고 lock2를 중첩으로 취득)인데 , 즉
//hold and wait(점유 대기)가 발생하는데 중첩하지 않고 따로 따로 떼어내서 사용한다면 점유 대기가 생기지 않기 떄문에 데드락을 발생X