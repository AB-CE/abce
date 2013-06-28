tryCatch(library(RSQLite), error = function(e) install.packages('RSQLite'))
tryCatch(library(reshape), error = function(e) install.packages('reshape'))

print("functions:")
print("sam_cell(seller, buyer, cell='quantity'), returns you the evolution over time of a cell")
sam_cell <- function(seller, buyer, cell='quantity', target=trade_unified) {
	ret <- target[which (trade_unified$seller==seller & trade_unified$buyer==buyer),c('round', cell)]
	ret
}
print("trade_over_time(seller, buyer, good, cell='quantity'), returns you the evolution over time of a cell")
trade_over_time <- function(seller, buyer, good, cell='quantity') {
	ret <- trade_unified[
			which (trade_unified$seller==seller & trade_unified$buyer==buyer & trade_unified$good==good),c('round', cell)]
	ret
}
print("sam(t), returns the social accounting matrix at time t")
sam <- function (t=0, target=trade_unified, value='quantity') {
	cast(target[which(target$round == t),], seller + good ~ buyer, sum, margins=c("grand_row","grand_col"), value=value)
}

print("sam_ext(t), returns the social accounting matrix at time t for every individual agent")
sam_ext <- function (t=1) {
	cast(trade[which(trade$round == t),], seller + good ~ buyer, sum, margins=c("grand_row","grand_col"))
}


# ************************* MAIN **********************
print("Import:")
rm(list=ls())
m <-dbDriver("SQLite")
con <-dbConnect(m, dbname = 'database.db')
rs <-dbSendQuery(con, "SELECT name FROM sqlite_master WHERE type='table';")
table_index_lst <- fetch(rs, n = -1)
table_index <- unlist(table_index_lst)
for (i in 1:length(table_index)) {
	rs <-dbSendQuery(con, paste("select * from",  table_index[i]))
	assign(table_index[i], fetch(rs, n = -1))
}
dbHasCompleted(rs)
dbClearResult(rs)
dbListTables(con)
print(table_index_lst)
rm(con, rs, m, table_index_lst, table_index)

# print("Transformations:")
# print("Unify households in trade")
# tt <- trade
# seller_table_index_lst <- matrix(1, nrow=nrow(tt), ncol=1)
# for (i in 1:nrow(tt)) {
# 	seller_table_index_lst[i] = i
# 	if (unlist(strsplit(tt$seller[i], "_"))[1] == 'firm') {
# 		seller_table_index_lst[i] <-tt$seller[i]
# 	} else {
# 		seller_table_index_lst[i] <- unlist(strsplit(tt$seller[i], "_"))[1]
# 	}
# }

# buyer_table_index_lst <- matrix(1, nrow=nrow(tt), ncol=1)
# for (i in 1:nrow(tt)) {
# 	buyer_table_index_lst[i] = i
# 	if (unlist(strsplit(tt$buyer[i], "_"))[1] == 'firm') {
# 		buyer_table_index_lst[i] <- tt$buyer[i]
# 	} else {
# 		buyer_table_index_lst[i] <- unlist(strsplit(tt$buyer[i], "_"))[1]
# 	}
# }

# tt$buyer <- buyer_table_index_lst
# tt$seller <- seller_table_index_lst

# rm(seller_table_index_lst)
# rm(buyer_table_index_lst)
# rm(i)
# print('OK')
#print("Compress 'trade' to 'trade_unified'")
#trade_unified <- ddply(tt, c('round', 'buyer', 'seller','good'), summarize, quantity=sum(quantity), price=mean(price))
#rm(tt)
#print('OK')
#INTERACTIVE
# a <- 1
# i <-1
# while (a==1) {
# 	cc <- readChar('stdin', 1)
# 	if (cc == 'h') {i <- i - 1}
# 	if (cc == 't') {i <- i + 1}
# 	if (cc == 'x') {a <- 2}
# 	print(i)
# 	print(cast(trade_unified[which(trade_unified$round == i),], seller+good ~ buyer, sum,margins=c("grand_row","grand_col")))
# }




