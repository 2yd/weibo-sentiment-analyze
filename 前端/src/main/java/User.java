public class User {
    private String username;
    private String cloudname;

    @Override
    public String toString() {
        return "User{" +
                "username='" + username + '\'' +
                ", cloudname='" + cloudname + '\'' +
                '}';
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getCloudname() {
        return cloudname;
    }

    public void setCloudname(String cloudname) {
        this.cloudname = cloudname;
    }
}
