# Airline Web

## Introduction
This project, "Airline Web," serves as a hands-on learning experience in database management and web development. The website is built using Flask, a lightweight web framework in Python, and is integrated with Microsoft SQL Server for the database backend. Through this project, I aim to demonstrate and apply the concepts and techniques I've learned during my studies of databases.

## 使用者模式

使用者模式允許訪問者完成以下操作：

- **搜尋航班**：使用者可以輸入出發地、目的地、出發日期等信息，以查找適合的航班選項。
- **選擇航班**：使用者可以查看可用的航班列表，並選擇他們想要的選項。
- **訂購機票**：使用者可以將所選機票添加到購物車，然後進行結帳。
- **結帳**：使用者可以提供必要的個人信息和付款信息，然後確認訂單。
- **查看訂單**：使用者可以查看他們以前的訂單記錄，包括訂單詳細信息和付款狀態。

## 管理者模式

管理者模式允許特權用戶執行以下操作：

- **管理航班信息**：管理者可以添加、編輯或刪除航班信息，包括航班號、日期、時間、座位數量等。
- **查看訂單**：管理者可以查看所有訂單，包括用戶的個人信息、訂單狀態和付款信息。
- **處理訂單**：管理者可以更新訂單的狀態，例如確認付款、發送電子機票等。
- **管理用戶**：管理者可以查看和管理用戶帳戶，包括添加或刪除用戶，重置密碼，以及查看用戶訂單記錄。

## Preparation
- [Download Microsoft SQL Server Express Edition](https://www.microsoft.com/zh-tw/sql-server/sql-server-downloads)