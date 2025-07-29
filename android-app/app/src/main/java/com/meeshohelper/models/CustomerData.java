package com.meeshohelper.models;

public class CustomerData {
    private String name;
    private String address;
    private String orderInfo;

    public CustomerData(String name, String address, String orderInfo) {
        this.name = name;
        this.address = address;
        this.orderInfo = orderInfo;
    }

    public CustomerData(String name) {
        this.name = name;
        this.address = "";
        this.orderInfo = "";
    }

    // Getters
    public String getName() {
        return name;
    }

    public String getAddress() {
        return address;
    }

    public String getOrderInfo() {
        return orderInfo;
    }

    // Setters
    public void setName(String name) {
        this.name = name;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public void setOrderInfo(String orderInfo) {
        this.orderInfo = orderInfo;
    }

    @Override
    public String toString() {
        return "CustomerData{" +
                "name='" + name + '\'' +
                ", address='" + address + '\'' +
                ", orderInfo='" + orderInfo + '\'' +
                '}';
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        CustomerData that = (CustomerData) obj;
        return name != null ? name.equals(that.name) : that.name == null;
    }

    @Override
    public int hashCode() {
        return name != null ? name.hashCode() : 0;
    }
}