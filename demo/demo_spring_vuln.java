// filename: demo_spring_vuln.java
// language: Java (Spring-style pseudocode) — illustrative only


public class DemoController {
// Hardcoded secret (demo only)
private static final String JWT_SECRET = "DEMO_FAKE_JWT_SECRET";


// Insecure SQL concatenation (illustrative only)
public String findUser(String uname) {
// BAD: concatenating into SQL
String q = "SELECT * FROM users WHERE username = '" + uname + "'";
return "SIMULATED_QUERY: " + q;
}


// Insecure deserialization usage (illustration)
public Object unsafeDeserialize(byte[] bytes) {
// Illustrative: using Java deserialization on untrusted data is unsafe
// ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(bytes));
// return ois.readObject();
return "SIMULATED_DESERIALIZE";
}


// Missing authorization enforcement example
public String viewOrder(String currentUserId, String requestedOrderOwnerId) {
// If code compares only IDs from client side, it is vulnerable
if (requestedOrderOwnerId.equals(currentUserId)) {
return "SIMULATED: Owner view";
}
// Insecure fallback: returns resource without proper checks
return "SIMULATED: Potentially returned resource"; // intentionally incorrect for demo
}
}