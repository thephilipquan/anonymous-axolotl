package beerapp.model;

public class User extends Person {

    public User(String username) {
        super(username);
    }

    public String getUsername() {
        return this.username;
    }
}