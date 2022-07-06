public class Uid {
    private String username;

    public String getUsername() {
        return username;
    }

    @Override
    public String toString() {
        return "Uid{" +
                "username='" + username + '\'' +
                '}';
    }

    public void setUsername(String username) {
        this.username = username;
    }
}
